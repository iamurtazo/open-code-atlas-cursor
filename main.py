from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin import setup_admin
from database import create_tables, get_db
from middleware import AuthMiddleware
from models import Course
from routers.api.admin import user as admin_user_router
from routers.api.admin import course as admin_course_router
from routers.web.courses import router as web_courses_router
from routers.web.users import router as web_users_router

app = FastAPI(title="CodeAtlas", version="0.1.0")

# Admin panel (mounted at /admin)
setup_admin(app)

# Middleware
app.add_middleware(AuthMiddleware)

# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(admin_user_router.router)
app.include_router(admin_course_router.router)
app.include_router(web_users_router)
app.include_router(web_courses_router)


@app.on_event("startup")
async def startup():
    """Create database tables on startup (dev only — Alembic handles prod)."""
    await create_tables()


@app.get("/")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Course))
    courses = result.scalars().all()
    courses_by_id = {c.id: c for c in courses}

    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "user": request.state.user,
            "courses": courses,
            "courses_by_id": courses_by_id,
        },
    )
