from __future__ import annotations

from dataclasses import dataclass

from .fallbacks import build_fallback_clip_result


@dataclass(frozen=True)
class RecoveryOption:
    code: str
    label: str
    description: str


@dataclass(frozen=True)
class FallbackEngineResult:
    output_type: str
    reason: str
    recovery_options: list[RecoveryOption]
    fallback_clip_count: int


DEFAULT_RECOVERY_OPTIONS: tuple[RecoveryOption, ...] = (
    RecoveryOption("retry_render", "Retry render", "Try the render step again."),
    RecoveryOption("export_strategy", "Export strategy package", "Use timestamps, hooks, captions, and CTA without a rendered file."),
    RecoveryOption("copy_package", "Copy package", "Copy the full strategy package into your editor or workflow."),
    RecoveryOption("lower_quality_render", "Try lighter render", "Retry with a lighter render preset when available."),
)


def build_recovery_plan(*, reason: str, duration_seconds: int | None = None) -> FallbackEngineResult:
    fallback = build_fallback_clip_result(reason=reason, duration_seconds=duration_seconds)
    return FallbackEngineResult(
        output_type="strategy_only" if fallback.fallback_used else "rendered_ready",
        reason=fallback.reason,
        recovery_options=list(DEFAULT_RECOVERY_OPTIONS),
        fallback_clip_count=len(fallback.clips),
    )


def recovery_plan_dict(**kwargs: object) -> dict[str, object]:
    result = build_recovery_plan(
        reason=str(kwargs.get("reason") or "Generation degraded."),
        duration_seconds=int(kwargs.get("duration_seconds") or 90),
    )
    return {
        "output_type": result.output_type,
        "reason": result.reason,
        "fallback_clip_count": result.fallback_clip_count,
        "recovery_options": [option.__dict__.copy() for option in result.recovery_options],
    }
