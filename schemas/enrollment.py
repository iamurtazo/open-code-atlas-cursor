from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ── Enrollment Schemas ────────────────────────────────────────────────────────


class EnrollmentBrief(BaseModel):
    """Lightweight enrollment for nesting inside other responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    course_id: str
    enrolled_at: datetime
