# LWA Source POC Matrix Results

Generated: 2026-04-28 17:25:20
Base URL: `http://127.0.0.1:8000`
Client ID prefix: `poc-source-matrix-1777411365-84b2b0`
Summary: `14` passed, `0` failed, `0` skipped

## Matrix

| Case | Expected | Upload | Generate | Source Type | Rendered Clips | Playable URLs | Clean Fallback | Raw Error Leak | Result |
|---|---|---:|---:|---|---:|---:|---:|---:|---|
| MP4 video upload | video_upload | yes | yes | video_upload | 1 | 2 | n/a | no | PASS |
| MOV video upload | video_upload | yes | yes | video_upload | 1 | 2 | n/a | no | PASS |
| M4V video upload | video_upload | yes | yes | video_upload | 1 | 2 | n/a | no | PASS |
| WEBM video upload | video_upload | yes | yes | video_upload | 1 | 2 | n/a | no | PASS |
| MP3 audio upload | audio_upload | yes | yes | audio_upload | 1 | 2 | n/a | no | PASS |
| WAV audio upload | audio_upload | yes | yes | audio_upload | 1 | 2 | n/a | no | PASS |
| M4A audio upload | audio_upload | yes | yes | audio_upload | 1 | 2 | n/a | no | PASS |
| JPG image upload | image_upload | yes | yes | image_upload | 0 | 0 | n/a | no | PASS |
| PNG image upload | image_upload | yes | yes | image_upload | 0 | 0 | n/a | no | PASS |
| WEBP image upload | image_upload | yes | yes | image_upload | 0 | 0 | n/a | no | PASS |
| HEIC image upload | image_upload | yes | yes | image_upload | 0 | 0 | n/a | no | PASS |
| HEIF image upload | image_upload | yes | yes | image_upload | 0 | 0 | n/a | no | PASS |
| Prompt-only idea generation | prompt, idea | n/a | yes | prompt | 0 | 0 | n/a | no | PASS |
| Public YouTube URL best-effort fallback | url | n/a | yes | url | 1 | 2 | n/a | no | PASS |

## Details

### MP4 video upload

- ID: `upload_mp4`
- Kind: `upload`
- Expected mode: `video`
- Expected source types: `video_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_903bd06b26`
- Returned source type: `video_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_903bd06b26/clip_001.mp4`
  - `http://127.0.0.1:8000/generated/req_903bd06b26/clip_001_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_903bd06b26/clip_001_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_903bd06b26/clip_001.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_903bd06b26/clip_001_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_903bd06b26/clip_001_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`

### MOV video upload

- ID: `upload_mov`
- Kind: `upload`
- Expected mode: `video`
- Expected source types: `video_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_eeb70d0f8f`
- Returned source type: `video_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_eeb70d0f8f/clip_001.mp4`
  - `http://127.0.0.1:8000/generated/req_eeb70d0f8f/clip_001_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_eeb70d0f8f/clip_001_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_eeb70d0f8f/clip_001.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_eeb70d0f8f/clip_001_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_eeb70d0f8f/clip_001_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`

### M4V video upload

- ID: `upload_m4v`
- Kind: `upload`
- Expected mode: `video`
- Expected source types: `video_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_549283b0c4`
- Returned source type: `video_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_549283b0c4/clip_001.mp4`
  - `http://127.0.0.1:8000/generated/req_549283b0c4/clip_001_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_549283b0c4/clip_001_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_549283b0c4/clip_001.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_549283b0c4/clip_001_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_549283b0c4/clip_001_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`

### WEBM video upload

- ID: `upload_webm`
- Kind: `upload`
- Expected mode: `video`
- Expected source types: `video_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_354c457092`
- Returned source type: `video_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_354c457092/clip_001.mp4`
  - `http://127.0.0.1:8000/generated/req_354c457092/clip_001_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_354c457092/clip_001_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_354c457092/clip_001.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_354c457092/clip_001_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_354c457092/clip_001_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`

### MP3 audio upload

- ID: `upload_mp3`
- Kind: `upload`
- Expected mode: `audio`
- Expected source types: `audio_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_3eb25b121f`
- Returned source type: `audio_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_3eb25b121f/clip_001.mp4`
  - `http://127.0.0.1:8000/generated/req_3eb25b121f/clip_001_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_3eb25b121f/clip_001_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_3eb25b121f/clip_001.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_3eb25b121f/clip_001_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_3eb25b121f/clip_001_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`

### WAV audio upload

- ID: `upload_wav`
- Kind: `upload`
- Expected mode: `audio`
- Expected source types: `audio_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_1591918f20`
- Returned source type: `audio_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_1591918f20/clip_001.mp4`
  - `http://127.0.0.1:8000/generated/req_1591918f20/clip_001_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_1591918f20/clip_001_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_1591918f20/clip_001.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_1591918f20/clip_001_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_1591918f20/clip_001_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`

### M4A audio upload

- ID: `upload_m4a`
- Kind: `upload`
- Expected mode: `audio`
- Expected source types: `audio_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_d842804423`
- Returned source type: `audio_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_d842804423/clip_001.mp4`
  - `http://127.0.0.1:8000/generated/req_d842804423/clip_001_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_d842804423/clip_001_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_d842804423/clip_001.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_d842804423/clip_001_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_d842804423/clip_001_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`

### JPG image upload

- ID: `upload_jpg`
- Kind: `upload`
- Expected mode: `image`
- Expected source types: `image_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_34ce145d3c`
- Returned source type: `image_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `0`
- Strategy-only clip count: `1`
- Playable URL count: `0`
- Clean fallback: `False`
- Raw error leaked: `False`

### PNG image upload

- ID: `upload_png`
- Kind: `upload`
- Expected mode: `image`
- Expected source types: `image_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_999d0d9fe0`
- Returned source type: `image_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `0`
- Strategy-only clip count: `1`
- Playable URL count: `0`
- Clean fallback: `False`
- Raw error leaked: `False`

### WEBP image upload

- ID: `upload_webp`
- Kind: `upload`
- Expected mode: `image`
- Expected source types: `image_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_4ef4e17fb3`
- Returned source type: `image_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `0`
- Strategy-only clip count: `1`
- Playable URL count: `0`
- Clean fallback: `False`
- Raw error leaked: `False`

### HEIC image upload

- ID: `upload_heic`
- Kind: `upload`
- Expected mode: `image`
- Expected source types: `image_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_5ed852c626`
- Returned source type: `image_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `0`
- Strategy-only clip count: `1`
- Playable URL count: `0`
- Clean fallback: `False`
- Raw error leaked: `False`

### HEIF image upload

- ID: `upload_heif`
- Kind: `upload`
- Expected mode: `image`
- Expected source types: `image_upload`
- Upload accepted: `True`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_dc5cbbba3e`
- Returned source type: `image_upload`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `0`
- Strategy-only clip count: `1`
- Playable URL count: `0`
- Clean fallback: `False`
- Raw error leaked: `False`

### Prompt-only idea generation

- ID: `prompt_only`
- Kind: `prompt`
- Expected mode: `idea`
- Expected source types: `prompt, idea`
- Upload accepted: `False`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_533349dbc7`
- Returned source type: `prompt`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `0`
- Strategy-only clip count: `1`
- Playable URL count: `0`
- Clean fallback: `False`
- Raw error leaked: `False`

### Public YouTube URL best-effort fallback

- ID: `youtube_public_url`
- Kind: `public_url`
- Expected mode: `url`
- Expected source types: `url`
- Upload accepted: `False`
- Generate accepted: `True`
- HTTP status: `200`
- Request ID: `req_b38bbf7e36`
- Returned source type: `url`
- Source type OK: `True`
- Clip count: `1`
- Rendered clip count: `1`
- Strategy-only clip count: `0`
- Playable URL count: `2`
- Clean fallback: `False`
- Raw error leaked: `False`
- Rendered/media URLs:
  - `http://127.0.0.1:8000/generated/req_b38bbf7e36/clip_005.mp4`
  - `http://127.0.0.1:8000/generated/req_b38bbf7e36/clip_005_preview.jpg`
  - `http://127.0.0.1:8000/generated/req_b38bbf7e36/clip_005_raw.mp4`
- Rendered URL checks:
  - `http://127.0.0.1:8000/generated/req_b38bbf7e36/clip_005.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
  - `http://127.0.0.1:8000/generated/req_b38bbf7e36/clip_005_preview.jpg` status=`200` content_type=`image/jpeg` playable=`False` error=`None`
  - `http://127.0.0.1:8000/generated/req_b38bbf7e36/clip_005_raw.mp4` status=`200` content_type=`video/mp4` playable=`True` error=`None`
