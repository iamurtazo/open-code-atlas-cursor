from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Course
from schemas import *

router = APIRouter(prefix="/api/admin", tags=["admin - courses"])

DB = Annotated[AsyncSession, Depends(get_db)]


# ── GET /api/admin/courses ───────────────────────────────────────────────────


@router.get("/courses", response_model=list[CourseResponse])
async def list_courses(
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    """List all courses with pagination."""

    stmt = select(Course).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# ── POST /api/admin/courses ──────────────────────────────────────────────────


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course_in: CourseCreate, db: DB):
    """Create a new course. Title must be unique (case-insensitive)."""

    # Check title uniqueness
    result = await db.execute(
        select(Course).where(func.lower(Course.title) == course_in.title.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Course with title '{course_in.title}' already exists",
        )

    course = Course(
        title=course_in.title,
        description=course_in.description,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


# ── GET /api/admin/courses/{course_id} ───────────────────────────────────────


@router.get("/courses/{course_id}", response_model=CourseResponse | CourseWithUsers)
async def get_course(
    course_id: str,
    db: DB,
    load_enrollments: bool = Query(default=False),
):
    """Fetch a single course by ID. Optionally eager-load enrollments."""

    stmt = select(Course).where(Course.id == course_id)

    if load_enrollments:
        stmt = stmt.options(selectinload(Course.enrollments))

    result = await db.execute(stmt)
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id '{course_id}' not found",
        )

    return course


# ── PATCH /api/admin/courses/{course_id} ─────────────────────────────────────


@router.patch("/courses/{course_id}", response_model=CourseResponse)
async def update_course(course_id: str, course_in: CourseUpdate, db: DB):
    """Update a course. Only provided fields are changed."""

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id '{course_id}' not found",
        )

    update_data = course_in.model_dump(exclude_unset=True)

    # Check title uniqueness if being changed
    if "title" in update_data:
        result = await db.execute(
            select(Course).where(
                func.lower(Course.title) == update_data["title"].lower(),
                Course.id != course_id,
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Course with title '{update_data['title']}' already exists",
            )

    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)
    return course


# ── DELETE /api/admin/courses/{course_id} ────────────────────────────────────


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: str, db: DB):
    """Delete a course by ID."""

    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id '{course_id}' not found",
        )

    await db.delete(course)
    await db.commit()
