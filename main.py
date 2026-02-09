from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import create_tables
from middleware import AuthMiddleware
from routers.api.admin import user as admin_user_router
from routers.api.admin import course as admin_course_router
from routers.web.users import router as web_users_router

app = FastAPI(title="CodeAtlas", version="0.1.0")

# Middleware
app.add_middleware(AuthMiddleware)

# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(admin_user_router.router)
app.include_router(admin_course_router.router)
app.include_router(web_users_router)


@app.on_event("startup")
async def startup():
    """Create database tables on startup (dev only — Alembic handles prod)."""
    await create_tables()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "base.html", {"request": request, "user": request.state.user}
    )
