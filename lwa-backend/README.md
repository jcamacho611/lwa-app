# LWA Backend

FastAPI backend for the LWA / IWA project.

This directory is the only Railway deployment target in the repo.

## Railway

- Root Directory: `lwa-backend/`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Builder: Nixpacks
- `nixpacks.toml` installs `ffmpeg` for Railway runtime
- Default video encoding is software `libx264` for higher-quality creator exports
- Set `LWA_VIDEO_ENCODER=mac` only if you explicitly want `h264_videotoolbox` on macOS development machines

## Local Run

```bash
cd lwa-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Required Endpoints

- `GET /`
- `GET /health`
- `POST /generate`
- `POST /process`
- `POST /v1/jobs`
