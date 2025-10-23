"""
Lesson API Tests

Integration tests for Lesson API endpoints
"""
import pytest
from datetime import date, timedelta
import uuid
from httpx import AsyncClient

from main import app
from models import Teacher, Class, Subject


@pytest.fixture
async def test_teacher(test_session, test_school, test_teacher_user):
    """Create a test teacher"""
    teacher = Teacher(
        id=uuid.UUID("fa4a570e-6ced-42e8-ab2f-beaf59b11a89"),
        school_id=test_school.id,
        user_id=test_teacher_user.id,
        employee_id="T001",
        hire_date=date(2023, 1, 1),
        status="active",
        is_active=True
    )
    test_session.add(teacher)
    await test_session.commit()
    await test_session.refresh(teacher)
    return teacher


@pytest.fixture
async def test_subject(test_session, test_school):
    """Create a test subject"""
    subject = Subject(
        id=uuid.UUID("94473bd5-c1de-4e8c-9ef3-bde10cacc143"),
        school_id=test_school.id,
        code="MATH",
        name="Mathematics",
        description="Mathematics subject",
        grade_levels=[5],
        is_active=True
    )
    test_session.add(subject)
    await test_session.commit()
    await test_session.refresh(subject)
    return subject


@pytest.fixture
async def test_class(test_session, test_school, test_teacher, test_subject):
    """Create a test class"""
    test_class = Class(
        id=uuid.UUID("2e008ff4-dc05-4c6b-8059-ca92fceb3f9a"),
        school_id=test_school.id,
        name="Math Grade 5 Q1",
        code="MATH-5-Q1",
        grade_level=5,
        quarter="Q1",
        academic_year="2024-2025",
        teacher_id=test_teacher.id,
        subject_id=test_subject.id,
        max_students=30,
        is_active=True
    )
    test_session.add(test_class)
    await test_session.commit()
    await test_session.refresh(test_class)
    return test_class


@pytest.fixture
async def client():
    """Create async HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestLessonAPI:
    """Test suite for Lesson API endpoints"""

    @pytest.mark.asyncio
    async def test_create_lesson(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test POST /api/v1/lessons - Create lesson"""
        lesson_data = {
            "title": "Introduction to Fractions",
            "description": "Learning about fractions",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": (date.today() + timedelta(days=7)).isoformat(),
            "duration_minutes": 45,
            "learning_objectives": ["Understand fractions", "Identify numerator"],
            "materials_needed": ["Fraction strips", "Whiteboard"]
        }

        response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Introduction to Fractions"
        assert data["lesson_number"] >= 1  # May be higher if previous tests ran
        assert data["status"] == "draft"
        assert len(data["learning_objectives"]) == 2

    @pytest.mark.asyncio
    async def test_create_lesson_invalid_title(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test creating lesson with invalid title"""
        lesson_data = {
            "title": "",  # Invalid: empty
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )

        assert response.status_code in [400, 422]  # 400 or 422 Unprocessable Entity

    @pytest.mark.asyncio
    async def test_get_lessons(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test GET /api/v1/lessons - List lessons"""
        # Create a lesson first
        lesson_data = {
            "title": "Test Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )

        # Get lessons
        response = await client.get(f"/api/v1/lessons?school_id={test_school.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1  # At least one lesson exists
        assert len(data["lessons"]) >= 1

    @pytest.mark.asyncio
    async def test_get_lesson_by_id(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test GET /api/v1/lessons/{id} - Get lesson by ID"""
        # Create a lesson
        lesson_data = {
            "title": "Test Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        create_response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )
        lesson_id = create_response.json()["id"]

        # Get the lesson
        response = await client.get(f"/api/v1/lessons/{lesson_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lesson_id
        assert data["title"] == "Test Lesson"

    @pytest.mark.asyncio
    async def test_update_lesson(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test PUT /api/v1/lessons/{id} - Update lesson"""
        # Create a lesson
        lesson_data = {
            "title": "Original Title",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        create_response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )
        lesson_id = create_response.json()["id"]

        # Update the lesson
        update_data = {
            "title": "Updated Title",
            "duration_minutes": 60
        }

        response = await client.put(
            f"/api/v1/lessons/{lesson_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["duration_minutes"] == 60

    @pytest.mark.asyncio
    async def test_start_lesson(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test POST /api/v1/lessons/{id}/start - Start lesson"""
        # Create a lesson
        lesson_data = {
            "title": "Test Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        create_response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )
        lesson_id = create_response.json()["id"]

        # Start the lesson
        response = await client.post(f"/api/v1/lessons/{lesson_id}/start")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_complete_lesson(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test POST /api/v1/lessons/{id}/complete - Complete lesson"""
        # Create and start a lesson
        lesson_data = {
            "title": "Test Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        create_response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )
        lesson_id = create_response.json()["id"]

        await client.post(f"/api/v1/lessons/{lesson_id}/start")

        # Complete the lesson
        complete_data = {
            "completion_percentage": 100,
            "actual_duration_minutes": 50,
            "what_went_well": "Students engaged well",
            "what_to_improve": "Need more examples"
        }

        response = await client.post(
            f"/api/v1/lessons/{lesson_id}/complete",
            json=complete_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completion_percentage"] == 100
        assert data["what_went_well"] == "Students engaged well"

    @pytest.mark.asyncio
    async def test_cancel_lesson(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test POST /api/v1/lessons/{id}/cancel - Cancel lesson"""
        # Create a lesson
        lesson_data = {
            "title": "Test Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        create_response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )
        lesson_id = create_response.json()["id"]

        # Cancel the lesson
        response = await client.post(f"/api/v1/lessons/{lesson_id}/cancel")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_delete_lesson(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test DELETE /api/v1/lessons/{id} - Delete lesson"""
        # Create a lesson
        lesson_data = {
            "title": "Test Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        create_response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )
        lesson_id = create_response.json()["id"]

        # Delete the lesson
        response = await client.delete(f"/api/v1/lessons/{lesson_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/v1/lessons/{lesson_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_statistics(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test GET /api/v1/lessons/statistics - Get statistics"""
        # Create some lessons
        for i in range(3):
            lesson_data = {
                "title": f"Lesson {i+1}",
                "class_id": str(test_class.id),
                "teacher_id": str(test_teacher.id),
                "subject_id": str(test_subject.id),
                "scheduled_date": date.today().isoformat(),
                "duration_minutes": 45
            }
            await client.post(
                f"/api/v1/lessons?school_id={test_school.id}",
                json=lesson_data
            )

        # Get statistics
        response = await client.get(
            f"/api/v1/lessons/statistics?school_id={test_school.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_lessons"] >= 3  # At least 3 lessons created in this test

    @pytest.mark.asyncio
    async def test_search_lessons(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test GET /api/v1/lessons/search - Search lessons"""
        # Create lessons
        lesson_data = {
            "title": "Introduction to Fractions",
            "description": "Learning fractions",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )

        # Search
        response = await client.get(
            f"/api/v1/lessons/search?school_id={test_school.id}&query=fractions"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1  # At least one result matching "fractions"

    @pytest.mark.asyncio
    async def test_convert_to_template(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test POST /api/v1/lessons/{id}/convert-to-template"""
        # Create a lesson
        lesson_data = {
            "title": "Template Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        create_response = await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=lesson_data
        )
        lesson_id = create_response.json()["id"]

        # Convert to template
        response = await client.post(
            f"/api/v1/lessons/{lesson_id}/convert-to-template"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_template"] is True

    @pytest.mark.asyncio
    async def test_filter_by_status(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test filtering lessons by status"""
        # Create lessons with different statuses
        draft_data = {
            "title": "Draft Lesson",
            "class_id": str(test_class.id),
            "teacher_id": str(test_teacher.id),
            "subject_id": str(test_subject.id),
            "scheduled_date": date.today().isoformat(),
            "duration_minutes": 45
        }

        await client.post(
            f"/api/v1/lessons?school_id={test_school.id}",
            json=draft_data
        )

        # Get lessons filtered by status
        response = await client.get(
            f"/api/v1/lessons?school_id={test_school.id}&status=draft"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for lesson in data["lessons"]:
            assert lesson["status"] == "draft"

    @pytest.mark.asyncio
    async def test_pagination(
        self, client, test_school, test_class, test_teacher, test_subject
    ):
        """Test lesson list pagination"""
        # Create multiple lessons
        for i in range(5):
            lesson_data = {
                "title": f"Lesson {i+1}",
                "class_id": str(test_class.id),
                "teacher_id": str(test_teacher.id),
                "subject_id": str(test_subject.id),
                "scheduled_date": date.today().isoformat(),
                "duration_minutes": 45
            }
            await client.post(
                f"/api/v1/lessons?school_id={test_school.id}",
                json=lesson_data
            )

        # Get first page
        response = await client.get(
            f"/api/v1/lessons?school_id={test_school.id}&page=1&limit=2"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 2
        assert len(data["lessons"]) == 2  # Limit enforces exactly 2
        assert data["total"] >= 5  # At least 5 lessons total
        assert data["pages"] >= 3  # At least 3 pages
