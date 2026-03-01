from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import func, select

from config import settings
from core.security import hash_password, verify_password
from database import AsyncSessionLocal, engine
from models import User, Course, Enrollment, Lesson


# ── Authentication ───────────────────────────────────────────────────────────


class AdminAuth(AuthenticationBackend):
    """Session-based admin authentication using existing User credentials."""

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(func.lower(User.username) == str(username).lower())
            )
            user = result.scalars().first()

        if not user or not verify_password(str(password), user.hashed_password):
            return False

        request.session.update({"user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("user_id"))


# ── Model Views ──────────────────────────────────────────────────────────────


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    # List page
    column_list = [
        User.id, User.username, User.email,
        User.first_name, User.last_name, User.created_at,
    ]
    column_searchable_list = [User.username, User.email, User.first_name, User.last_name]
    column_sortable_list = [User.username, User.email, User.created_at]
    column_default_sort = (User.created_at, True)

    # Detail page — never expose the hash
    column_details_exclude_list = [User.hashed_password]

    # Forms — exclude auto-managed fields and relationships
    form_excluded_columns = [User.id, User.created_at, User.updated_at, User.enrollments]

    async def on_model_change(self, data: dict, model: User, is_created: bool, request: Request) -> None:
        """Hash the plain-text password before it reaches the database."""
        if "hashed_password" in data and data["hashed_password"]:
            data["hashed_password"] = hash_password(data["hashed_password"])


class CourseAdmin(ModelView, model=Course):
    name = "Course"
    name_plural = "Courses"
    icon = "fa-solid fa-book"

    # List page
    column_list = [
        Course.id, Course.title, Course.category,
        Course.youtube_playlist_id, Course.lesson_count, Course.created_at,
    ]
    column_searchable_list = [Course.title, Course.category]
    column_sortable_list = [Course.title, Course.category, Course.created_at]
    column_default_sort = (Course.created_at, True)

    # Forms
    form_excluded_columns = [Course.id, Course.created_at, Course.updated_at, Course.enrollments, Course.lessons]


class LessonAdmin(ModelView, model=Lesson):
    name = "Lesson"
    name_plural = "Lessons"
    icon = "fa-solid fa-play"

    column_list = [
        Lesson.id, Lesson.position, Lesson.title,
        Lesson.youtube_video_id, Lesson.duration_seconds, Lesson.course_id,
    ]
    column_searchable_list = [Lesson.title]
    column_sortable_list = [Lesson.position, Lesson.title, Lesson.course_id]
    column_default_sort = (Lesson.position, False)

    form_excluded_columns = [Lesson.id, Lesson.created_at]


class EnrollmentAdmin(ModelView, model=Enrollment):
    name = "Enrollment"
    name_plural = "Enrollments"
    icon = "fa-solid fa-graduation-cap"

    # List page
    column_list = [Enrollment.id, Enrollment.user_id, Enrollment.course_id, Enrollment.enrolled_at]
    column_sortable_list = [Enrollment.enrolled_at]
    column_default_sort = (Enrollment.enrolled_at, True)

    # Forms
    form_excluded_columns = [Enrollment.id, Enrollment.enrolled_at]


# ── Setup helper ─────────────────────────────────────────────────────────────


def setup_admin(app) -> Admin:
    """Mount the sqladmin panel on the FastAPI app at /admin."""
    authentication_backend = AdminAuth(secret_key=settings.secret_key.get_secret_value())
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="CodeAtlas Admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(CourseAdmin)
    admin.add_view(EnrollmentAdmin)
    admin.add_view(LessonAdmin)
    return admin
