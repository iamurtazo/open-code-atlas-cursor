from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── User Schemas ──────────────────────────────────────────────────────────────


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr = Field(max_length=100)
    first_name: str | None = Field(default=None, max_length=70)
    last_name: str | None = Field(default=None, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user. No password — auth is Phase 2."""

    pass


class UserUpdate(BaseModel):
    """Schema for partial updates. All fields optional."""

    username: str | None = Field(default=None, min_length=3, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=100)
    first_name: str | None = Field(default=None, max_length=70)
    last_name: str | None = Field(default=None, max_length=100)


class UserProfile(BaseModel):
    """Public-facing user response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    created_at: datetime
    updated_at: datetime


class UserAdmin(BaseModel):
    """Full admin view — includes all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    created_at: datetime
    updated_at: datetime
