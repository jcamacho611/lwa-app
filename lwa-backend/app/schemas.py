from pydantic import BaseModel, Field, HttpUrl


class ProcessRequest(BaseModel):
    video_url: HttpUrl = Field(..., description="Public URL for the source video")


class ClipResult(BaseModel):
    id: str
    title: str
    hook: str
    caption: str
    start_time: str
    end_time: str


class ClipBatchResponse(BaseModel):
    video_url: HttpUrl
    status: str
    clips: list[ClipResult]

