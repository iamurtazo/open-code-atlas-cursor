from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import User
from schemas import UserCreate, UserProfile, UserUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])

DB = Annotated[AsyncSession, Depends(get_db)]


# ── POST /api/admin/users ────────────────────────────────────────────────────


@router.post("/users", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: DB):
    """Create a new user. Username and email must be unique (case-insensitive)."""

    # Check username uniqueness
    result = await db.execute(
        select(User).where(func.lower(User.username) == user_in.username.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_in.username}' is already taken",
        )

    # Check email uniqueness
    result = await db.execute(
        select(User).where(func.lower(User.email) == user_in.email.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_in.email}' is already registered",
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ── GET /api/admin/users/{user_id} ───────────────────────────────────────────


@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: str,
    db: DB,
    load_enrollments: bool = Query(default=False),
):
    """Fetch a single user by ID. Optionally eager-load enrollments."""

    stmt = select(User).where(User.id == user_id)

    if load_enrollments:
        stmt = stmt.options(selectinload(User.enrollments))

    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )

    return user


# ── GET /api/admin/users ─────────────────────────────────────────────────────


@router.get("/users", response_model=list[UserProfile])
async def list_users(
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    load_enrollments: bool = Query(default=False),
):
    """List all users with pagination. Optionally eager-load enrollments."""

    stmt = select(User).offset(skip).limit(limit)

    if load_enrollments:
        stmt = stmt.options(selectinload(User.enrollments))

    result = await db.execute(stmt)
    return result.scalars().all()


# ── PUT /api/admin/users/{user_id} ───────────────────────────────────────────


@router.patch("/users/{user_id}", response_model=UserProfile)
async def update_user(user_id: str, user_in: UserUpdate, db: DB):
    """Update a user. Only provided fields are changed."""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )

    update_data = user_in.model_dump(exclude_unset=True)

    # Check username uniqueness if being changed
    if "username" in update_data:
        result = await db.execute(
            select(User).where(
                func.lower(User.username) == update_data["username"].lower(),
                User.id != user_id,
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{update_data['username']}' is already taken",
            )

    # Check email uniqueness if being changed
    if "email" in update_data:
        result = await db.execute(
            select(User).where(
                func.lower(User.email) == update_data["email"].lower(),
                User.id != user_id,
            )
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{update_data['email']}' is already registered",
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


# ── DELETE /api/admin/users/{user_id} ────────────────────────────────────────


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: DB):
    """Delete a user by ID."""

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found",
        )

    await db.delete(user)
    await db.commit()
