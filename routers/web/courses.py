from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Course, Lesson

router = APIRouter(tags=["web-courses"])
templates = Jinja2Templates(directory="templates")

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/course/{course_id}")
async def course_page(course_id: str, request: Request, db: DB, v: str | None = None):
    """
    Render the course detail page.
    Optional query param `v` selects a specific video by youtube_video_id.
    """
    result = await db.execute(
        select(Course)
        .where(Course.id == course_id)
        .options(selectinload(Course.lessons))
    )
    course = result.scalars().first()

    if not course or not course.lessons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    lessons = sorted(course.lessons, key=lambda l: l.position)

    if v:
        active_lesson = next((l for l in lessons if l.youtube_video_id == v), lessons[0])
    else:
        active_lesson = lessons[0]

    return templates.TemplateResponse(
        "course.html",
        {
            "request": request,
            "user": request.state.user,
            "course": course,
            "lessons": lessons,
            "active_lesson": active_lesson,
            "active_video_id": active_lesson.youtube_video_id,
        },
    )
