from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy import select

from database import AsyncSessionLocal
from models.user import User


class AuthMiddleware(BaseHTTPMiddleware):
    """Read user_id cookie on every request and attach the User to request.state."""

    async def dispatch(self, request: Request, call_next):
        request.state.user = None

        user_id = request.cookies.get("user_id")
        if user_id:
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(
                        select(User).where(User.id == user_id)
                    )
                    request.state.user = result.scalars().first()
            except (ValueError, Exception):
                pass

        response = await call_next(request)
        return response
