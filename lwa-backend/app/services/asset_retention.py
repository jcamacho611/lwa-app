"""
LWA generated asset retention cleanup.

Purpose:
- Keep Railway generated-assets volume from filling up.
- Delete old generated media and artifact files safely.
- Never delete outside the configured generated assets directory.
- Never crash the app if cleanup fails.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import logging
import os
from pathlib import Path
from typing import Any, Iterable

from ..core.config import Settings
from .generated_asset_store import GeneratedAssetStore

logger = logging.getLogger("uvicorn.error")


@dataclass(frozen=True)
class AssetRetentionResult:
    scanned_count: int = 0
    deleted_count: int = 0
    skipped_count: int = 0
    retained_count: int = 0
    bytes_deleted: int = 0
    errors: tuple[str, ...] = ()
    deleted_paths: tuple[str, ...] = ()
    expired_deleted_count: int = 0
    overflow_deleted_count: int = 0
    protected_skipped_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["errors"] = list(self.errors)
        payload["deleted_paths"] = list(self.deleted_paths)
        payload.update(
            {
                "scanned": self.scanned_count,
                "removed": self.deleted_count,
                "expired_removed": self.expired_deleted_count,
                "overflow_removed": self.overflow_deleted_count,
                "protected_skipped": self.protected_skipped_count,
                "removed_paths": list(self.deleted_paths),
            }
        )
        return payload


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def _is_inside_directory(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def _file_modified_at(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def _iter_files(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []

    files: list[Path] = []
    for root, _, filenames in os.walk(directory):
        root_path = Path(root)
        for filename in filenames:
            files.append(root_path / filename)
    return files


def _prune_empty_directories(base_dir: Path) -> None:
    for root, dirnames, _ in os.walk(base_dir, topdown=False):
        root_path = Path(root)
        for dirname in dirnames:
            candidate = root_path / dirname
            try:
                resolved_candidate = _safe_resolve(candidate)
            except Exception:
                continue
            if not _is_inside_directory(resolved_candidate, base_dir):
                continue
            try:
                candidate.rmdir()
            except OSError:
                continue


def cleanup_generated_assets(
    generated_assets_dir: str | Path,
    *,
    retention_hours: int = 24,
    max_files: int = 300,
    now: datetime | None = None,
    protected_paths: Iterable[str | Path] = (),
) -> AssetRetentionResult:
    """
    Cleanup generated assets safely.

    Deletes:
    1. Files older than retention_hours.
    2. Oldest remaining files if file count exceeds max_files.

    Does not:
    - delete outside generated_assets_dir
    - raise exceptions to caller
    - delete non-empty directories directly
    """

    errors: list[str] = []
    deleted_paths: list[str] = []
    skipped_count = 0
    protected_skipped_count = 0
    deleted_count = 0
    expired_deleted_count = 0
    overflow_deleted_count = 0
    bytes_deleted = 0

    try:
        base_dir = _safe_resolve(Path(generated_assets_dir))
    except Exception as exc:
        return AssetRetentionResult(
            skipped_count=1,
            errors=(f"failed_to_resolve_directory:{exc}",),
        )

    if not base_dir.exists():
        return AssetRetentionResult()

    if not base_dir.is_dir():
        return AssetRetentionResult(
            skipped_count=1,
            errors=(f"not_a_directory:{base_dir}",),
        )

    safe_retention_hours = max(int(retention_hours), 1)
    safe_max_files = max(int(max_files), 1)
    effective_now = now or _utc_now()
    cutoff = effective_now - timedelta(hours=safe_retention_hours)

    protected: set[Path] = set()
    for protected_path in protected_paths:
        try:
            candidate = str(protected_path).strip()
            if not candidate:
                continue
            protected.add(_safe_resolve(Path(candidate)))
        except Exception as exc:
            errors.append(f"protected_path_invalid:{protected_path}:{exc}")

    files = _iter_files(base_dir)
    scanned_count = len(files)
    remaining_files: list[Path] = []

    for file_path in files:
        try:
            resolved_file = _safe_resolve(file_path)

            if not _is_inside_directory(resolved_file, base_dir):
                skipped_count += 1
                errors.append(f"outside_base_skipped:{resolved_file}")
                continue

            if resolved_file in protected:
                skipped_count += 1
                protected_skipped_count += 1
                continue

            if not resolved_file.exists() or not resolved_file.is_file():
                skipped_count += 1
                continue

            modified_at = _file_modified_at(resolved_file)
            if modified_at < cutoff:
                file_size = resolved_file.stat().st_size
                resolved_file.unlink()
                deleted_count += 1
                expired_deleted_count += 1
                bytes_deleted += file_size
                deleted_paths.append(str(resolved_file))
            else:
                remaining_files.append(resolved_file)
        except Exception as exc:
            skipped_count += 1
            errors.append(f"delete_old_failed:{file_path}:{exc}")

    if len(remaining_files) > safe_max_files:
        try:
            survivors = [
                path
                for path in remaining_files
                if path.exists()
                and path.is_file()
                and path not in protected
                and _is_inside_directory(path, base_dir)
            ]
            survivors.sort(key=lambda path: (path.stat().st_mtime, str(path)))
            overflow_count = max(len(survivors) - safe_max_files, 0)
            for file_path in survivors[:overflow_count]:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    overflow_deleted_count += 1
                    bytes_deleted += file_size
                    deleted_paths.append(str(file_path))
                except Exception as exc:
                    skipped_count += 1
                    errors.append(f"delete_overflow_failed:{file_path}:{exc}")
        except Exception as exc:
            errors.append(f"max_file_trim_failed:{exc}")

    try:
        _prune_empty_directories(base_dir)
    except Exception as exc:
        errors.append(f"prune_empty_directories_failed:{exc}")

    try:
        retained_count = len(_iter_files(base_dir))
    except Exception as exc:
        errors.append(f"retained_count_failed:{exc}")
        retained_count = 0

    result = AssetRetentionResult(
        scanned_count=scanned_count,
        deleted_count=deleted_count,
        skipped_count=skipped_count,
        retained_count=retained_count,
        bytes_deleted=bytes_deleted,
        errors=tuple(errors),
        deleted_paths=tuple(deleted_paths),
        expired_deleted_count=expired_deleted_count,
        overflow_deleted_count=overflow_deleted_count,
        protected_skipped_count=protected_skipped_count,
    )
    logger.info("generated_asset_cleanup_complete %s", result.to_dict())
    return result


def cleanup_generated_assets_nonfatal(
    generated_assets_dir: str | Path,
    *,
    retention_hours: int = 24,
    max_files: int = 300,
    protected_paths: Iterable[str | Path] = (),
) -> AssetRetentionResult:
    try:
        return cleanup_generated_assets(
            generated_assets_dir,
            retention_hours=retention_hours,
            max_files=max_files,
            protected_paths=protected_paths,
        )
    except Exception as exc:
        logger.exception("generated_asset_cleanup_nonfatal_failed error=%s", exc)
        return AssetRetentionResult(
            skipped_count=1,
            errors=(f"nonfatal_cleanup_failed:{exc}",),
        )


def cleanup_generated_assets_for_settings(settings: Settings) -> dict[str, Any]:
    result = cleanup_generated_assets(
        settings.generated_assets_dir,
        retention_hours=settings.generated_asset_retention_hours,
        max_files=settings.generated_assets_max_files,
        protected_paths=(
            settings.generated_asset_store_path,
            settings.usage_store_path,
            settings.platform_db_path,
            settings.clipping_db_path,
            settings.event_log_path,
        ),
    )
    payload = result.to_dict()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max(settings.generated_asset_retention_hours, 1))
    try:
        asset_store = GeneratedAssetStore(settings.generated_asset_store_path)
        payload["store_removed"] = asset_store.prune_assets(
            stale_before=cutoff.isoformat(),
            removed_local_paths=list(result.deleted_paths),
        )
    except Exception as exc:
        logger.warning("generated_asset_store_cleanup_failed error=%s", exc)
        payload["store_removed"] = 0
        payload["errors"] = [*payload.get("errors", []), f"store_cleanup_failed:{exc}"]

    return payload


def cleanup_generated_assets_nonfatal_for_settings(settings: Settings) -> dict[str, Any]:
    try:
        return cleanup_generated_assets_for_settings(settings)
    except Exception as exc:
        logger.exception("generated_asset_cleanup_for_settings_nonfatal_failed error=%s", exc)
        payload = AssetRetentionResult(
            skipped_count=1,
            errors=(f"nonfatal_cleanup_failed:{exc}",),
        ).to_dict()
        payload["store_removed"] = 0
        return payload
