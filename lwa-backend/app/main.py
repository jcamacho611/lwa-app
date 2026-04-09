from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .mock_data import build_mock_clips
from .schemas import ClipBatchResponse, ProcessRequest

app = FastAPI(
    title="LWA Backend",
    version="0.1.0",
    description="Starter backend for local video clip mock processing.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/process", response_model=ClipBatchResponse)
async def process_video(request: ProcessRequest) -> ClipBatchResponse:
    return ClipBatchResponse(
        video_url=request.video_url,
        status="success",
        clips=build_mock_clips(str(request.video_url)),
    )

