"""
Test Configuration and Fixtures
Pytest configuration and shared fixtures for all tests
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import uuid

from config.database import Base
from models import User, School


# Test database URL (in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def test_school(test_session):
    """Create a test school"""
    school = School(
        id=uuid.UUID("60da2256-81fc-4ca5-bf6b-467b8d371c61"),
        name="Test School",
        slug="test-school",
        email="test@school.edu",
        phone="+1234567890",
        city="Test City",
        state="TS",
        status="active"
    )
    test_session.add(school)
    await test_session.commit()
    await test_session.refresh(school)
    return school


@pytest.fixture
async def test_admin_user(test_session, test_school):
    """Create a test administrator user"""
    user = User(
        id=uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499"),
        school_id=test_school.id,
        email="admin@test.edu",
        first_name="Admin",
        last_name="User",
        persona="administrator",
        status="active"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def test_teacher_user(test_session, test_school):
    """Create a test teacher user"""
    user = User(
        school_id=test_school.id,
        email="teacher@test.edu",
        first_name="Teacher",
        last_name="User",
        persona="teacher",
        status="active"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def test_student_user(test_session, test_school):
    """Create a test student user"""
    user = User(
        school_id=test_school.id,
        email="student@test.edu",
        first_name="Student",
        last_name="User",
        persona="student",
        status="active"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def test_users(test_session, test_school):
    """Create multiple test users"""
    users = []

    personas = ["administrator", "teacher", "student", "parent", "vendor"]
    for i, persona in enumerate(personas):
        user = User(
            school_id=test_school.id,
            email=f"{persona}{i}@test.edu",
            first_name=persona.capitalize(),
            last_name=f"User{i}",
            persona=persona,
            status="active"
        )
        test_session.add(user)
        users.append(user)

    await test_session.commit()

    for user in users:
        await test_session.refresh(user)

    return users
