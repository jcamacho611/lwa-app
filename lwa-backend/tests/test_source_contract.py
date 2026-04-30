from app.services.source_contract import (
    SOURCE_TYPE_AUDIO_UPLOAD,
    SOURCE_TYPE_CAMPAIGN,
    SOURCE_TYPE_IMAGE_UPLOAD,
    SOURCE_TYPE_PROMPT,
    SOURCE_TYPE_URL,
    SOURCE_TYPE_VIDEO_UPLOAD,
    classify_upload_source_type,
    is_allowed_upload,
    normalize_source_type,
    supported_upload_summary,
    upload_source_ref,
)


def test_supported_upload_summary_covers_launch_formats() -> None:
    summary = supported_upload_summary()
    assert ".mp4" in summary["video"]
    assert ".mov" in summary["video"]
    assert ".mp3" in summary["audio"]
    assert ".wav" in summary["audio"]
    assert ".jpg" in summary["image"]
    assert ".png" in summary["image"]


def test_classify_upload_source_type_prefers_mime_prefixes() -> None:
    assert classify_upload_source_type(filename="clip.bin", content_type="video/mp4") == SOURCE_TYPE_VIDEO_UPLOAD
    assert classify_upload_source_type(filename="audio.bin", content_type="audio/mpeg") == SOURCE_TYPE_AUDIO_UPLOAD
    assert classify_upload_source_type(filename="image.bin", content_type="image/png") == SOURCE_TYPE_IMAGE_UPLOAD


def test_classify_upload_source_type_falls_back_to_extension() -> None:
    assert classify_upload_source_type(filename="clip.webm", content_type=None) == SOURCE_TYPE_VIDEO_UPLOAD
    assert classify_upload_source_type(filename="clip.m4a", content_type=None) == SOURCE_TYPE_AUDIO_UPLOAD
    assert classify_upload_source_type(filename="clip.webp", content_type=None) == SOURCE_TYPE_IMAGE_UPLOAD


def test_upload_allowed_by_extension_or_content_type() -> None:
    assert is_allowed_upload(filename="clip.mp4", content_type="application/octet-stream")
    assert is_allowed_upload(filename="source.bin", content_type="audio/wav")
    assert not is_allowed_upload(filename="notes.txt", content_type="text/plain")


def test_normalize_source_type_aliases() -> None:
    assert normalize_source_type("public-url") == SOURCE_TYPE_URL
    assert normalize_source_type("text") == SOURCE_TYPE_PROMPT
    assert normalize_source_type("campaign-objective") == SOURCE_TYPE_CAMPAIGN
    assert normalize_source_type("video_upload") == SOURCE_TYPE_VIDEO_UPLOAD


def test_upload_source_ref_contains_stable_source_type() -> None:
    assert upload_source_ref(upload_id="up_123", source_type="video_upload") == {
        "source_kind": "upload",
        "source_type": SOURCE_TYPE_VIDEO_UPLOAD,
        "upload_id": "up_123",
    }
