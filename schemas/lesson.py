from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LessonBase(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    youtube_video_id: str = Field(min_length=1, max_length=20)
    position: int = Field(ge=1)
    duration_seconds: int = Field(default=0, ge=0)


class LessonCreate(LessonBase):
    course_id: str


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    youtube_video_id: str
    position: int
    duration_seconds: int
    course_id: str
    created_at: datetime
