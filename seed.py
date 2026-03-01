"""Seed the database with Neso Academy's C Programming playlist."""

import asyncio

from sqlalchemy import select

from database import AsyncSessionLocal, create_tables
from models import Course, Lesson

NESO_C_PLAYLIST = "PLBlnK6fEyqRggZZgYpPMUxdY1CYkZtARR"

LESSONS = [
    ("rLf3jnHxSmU", "C Programming \u2013 Features & The First C Program", 898),
    ("fO4FwJOShdc", "Introduction to Variables", 504),
    ("Rl9w0hVxuRw", "Variable Naming Conventions", 261),
    ("VXol2-SoUy8", "Basic Output Function \u2013 printf", 374),
    ("_9bAlgRzlkc", "Fundamental Data Types \u2212 Integer (Part 1)", 460),
    ("bUryucFPC6I", "Fundamental Data Types \u2212 Integer (Part 2)", 440),
    ("nwfoxcXgs8o", "Exceeding The Valid Range of Data Types", 467),
    ("QncEuobXjvw", "Fundamental Data Types \u2212 Character", 745),
    ("vNeOx1rQ25E", "Fundamental Data Types \u2212 Float, Double & Long Double", 786),
    ("IY79fWYkiPQ", "C Programming (Important Questions Set 1)", 822),
    ("elMQ5YtZPxA", "Scope of Variables - Local vs Global", 672),
    ("1Dkfmf4PmvQ", "Variable Modifiers \u2212 Auto & Extern", 772),
    ("qHZ7qf6-rhc", "Variable Modifiers \u2212 Register", 242),
    ("CRhF8a9-pzc", "Variable Modifiers \u2212 Static", 1142),
    ("BVnNg20AuYU", "Constants in C (Part 1)", 523),
    ("I1i0WgiRVXo", "Constants in C (Part 2)", 245),
    ("hTUvEURkNeA", "C Programming (Important Questions Set 2)", 370),
    ("ZSZwDARaQYI", "Basic Input Function \u2013 scanf", 308),
    ("gegaS_gX3TY", "C Programming (Important Questions Set 3)", 1279),
    ("50Pb27JoUrw", "Introduction to Operators in C", 333),
    ("5JXcX0IqRUo", "Arithmetic Operators in C", 482),
    ("Lpo1QYsuAmM", "Increment and Decrement Operators in C (Part 1)", 655),
    ("3uRoSITqXRI", "Increment and Decrement Operators in C (Part 2)", 939),
    ("1oKRTjw0yuY", "Relational Operators in C", 216),
    ("WGQRInmOBM8", "Logical Operators in C", 729),
    ("jlQmeyce65Q", "Bitwise Operators in C (Part 1)", 472),
    ("8aFik6lPPaA", "Bitwise Operators in C (Part 2)", 299),
    ("GhhJP6vpEA8", "Bitwise Operators in C (Part 3)", 241),
    ("kYR5biY4OHw", "Bitwise Operators in C (Part 4)", 274),
    ("zv73Qv1GdwY", "Assignment Operators in C", 288),
    ("rULDbIbrXis", "Conditional Operator in C", 341),
    ("mhmnb80ZDBM", "Comma Operator in C", 510),
    ("8H9G621pQq0", "Precedence and Associativity of Operators", 987),
    ("HAKAhma7MQg", "Operators in C (Solved Problem 1)", 354),
    ("-QXh0y__tYY", "Operators in C (Solved Problem 2)", 387),
    ("5sOZ7l2it2I", "C Programming (Rapid Fire Quiz-1)", 352),
    ("Led5aHdLoT4", "Conditionals (if-else, Nested if and else if)", 490),
    ("-JMSaLRqsgo", "Conditionals (Switch)", 444),
    ("qUPXsPtWGoY", "for and while Loops", 409),
    ("TjkJQly2YCw", "do-while Loop", 303),
]


async def seed():
    await create_tables()

    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(Course).where(Course.youtube_playlist_id == NESO_C_PLAYLIST)
        )
        if existing.scalars().first():
            print("C Programming course already seeded. Skipping.")
            return

        course = Course(
            title="C Programming",
            description="Complete C programming course by Neso Academy covering "
            "variables, data types, operators, control flow, and more.",
            youtube_playlist_id=NESO_C_PLAYLIST,
            category="Programming Languages",
            lesson_count=len(LESSONS),
        )
        session.add(course)
        await session.flush()

        for position, (video_id, title, duration) in enumerate(LESSONS, start=1):
            session.add(
                Lesson(
                    title=title,
                    youtube_video_id=video_id,
                    position=position,
                    duration_seconds=duration,
                    course_id=course.id,
                )
            )

        await session.commit()
        print(f"Seeded course '{course.title}' with {len(LESSONS)} lessons (id: {course.id})")


if __name__ == "__main__":
    asyncio.run(seed())
