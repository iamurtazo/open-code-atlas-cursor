from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import create_tables
from routers.api.admin import (
    router as admin_router,
)

app = FastAPI(title="CodeAtlas", version="0.1.0")

# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(admin_router)


@app.on_event("startup")
async def startup():
    """Create database tables on startup (dev only — Alembic handles prod)."""
    await create_tables()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
