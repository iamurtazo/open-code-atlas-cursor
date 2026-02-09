from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.enrollment import EnrollmentBrief


# ── Course Schemas ────────────────────────────────────────────────────────────


class CourseBase(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=2000)


class CourseCreate(CourseBase):
    """Schema for creating a new course."""

    pass


class CourseUpdate(BaseModel):
    """Schema for partial updates. All fields optional."""

    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=2000)


class CourseResponse(BaseModel):
    """Standard course response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class CourseWithUsers(CourseResponse):
    """Course response with nested enrollments."""

    enrollments: list[EnrollmentBrief] = []
