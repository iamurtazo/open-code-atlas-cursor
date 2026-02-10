from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, verify_password
from database import get_db
from models import User

router = APIRouter(tags=["web-auth"])
templates = Jinja2Templates(directory="templates")

DB = Annotated[AsyncSession, Depends(get_db)]


# ── GET /login ────────────────────────────────────────────────────────────────


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user": request.state.user})


# ── GET /signup ───────────────────────────────────────────────────────────────


@router.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "user": request.state.user})


# ── POST /signup ──────────────────────────────────────────────────────────────


@router.post("/signup")
async def signup(
    db: DB,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(default=None),
    last_name: str = Form(default=None),
):
    """Create a new user with hashed password and set session cookie."""

    # Check username uniqueness (case-insensitive)
    result = await db.execute(
        select(User).where(func.lower(User.username) == username.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{username}' is already taken",
        )

    # Check email uniqueness (case-insensitive)
    result = await db.execute(
        select(User).where(func.lower(User.email) == email.lower())
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{email}' is already registered",
        )

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        first_name=first_name or None,
        last_name=last_name or None,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    response = JSONResponse(
        content={"id": new_user.id, "username": new_user.username},
        status_code=status.HTTP_201_CREATED,
    )
    response.set_cookie(key="user_id", value=str(new_user.id), httponly=True)
    return response


# ── POST /login ───────────────────────────────────────────────────────────────


@router.post("/login")
async def login(
    db: DB,
    username: str = Form(...),
    password: str = Form(...),
):
    """Log in with username and password. Set session cookie on success."""

    result = await db.execute(
        select(User).where(func.lower(User.username) == username.lower())
    )
    user = result.scalars().first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    response = JSONResponse(
        content={"id": user.id, "username": user.username},
    )
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return response


# ── GET /signout ──────────────────────────────────────────────────────────────


@router.get("/signout")
async def signout():
    """Clear session cookie and redirect to home."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="user_id")
    return response


# ── GET /account ──────────────────────────────────────────────────────────────


@router.get("/account")
async def account_page(request: Request):
    """Show account page. Redirect to home if not authenticated."""
    if not request.state.user:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse(
        "account.html", {"request": request, "user": request.state.user}
    )
