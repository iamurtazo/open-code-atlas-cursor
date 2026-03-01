from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.course import Course


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    youtube_video_id: Mapped[str] = mapped_column(String(20), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    course_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("courses.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="lessons")

    @property
    def duration_display(self) -> str:
        """Format seconds as MM:SS."""
        m, s = divmod(self.duration_seconds, 60)
        return f"{m:02d}:{s:02d}"

    def __repr__(self) -> str:
        return f"<Lesson {self.position}: {self.title}>"
