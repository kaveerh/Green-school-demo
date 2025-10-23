"""
Lesson Repository Tests

Unit tests for LessonRepository data access layer
"""
import pytest
from datetime import date, timedelta
import uuid

from repositories.lesson_repository import LessonRepository
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
    from models import Class

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
async def lesson_repository(test_session):
    """Create a lesson repository instance"""
    return LessonRepository(test_session)


@pytest.fixture
async def sample_lesson_data(test_school, test_class, test_teacher, test_subject):
    """Sample lesson data for testing"""
    return {
        "school_id": test_school.id,
        "class_id": test_class.id,
        "teacher_id": test_teacher.id,
        "subject_id": test_subject.id,
        "title": "Introduction to Fractions",
        "lesson_number": 1,
        "scheduled_date": date.today() + timedelta(days=7),
        "duration_minutes": 45,
        "description": "Learning about fractions",
        "learning_objectives": ["Understand fractions", "Identify numerator"],
        "materials_needed": ["Fraction strips", "Whiteboard"],
        "status": "draft"
    }


class TestLessonRepository:
    """Test suite for LessonRepository"""

    @pytest.mark.asyncio
    async def test_create_lesson(self, lesson_repository, sample_lesson_data):
        """Test creating a lesson"""
        lesson = await lesson_repository.create(sample_lesson_data)

        assert lesson is not None
        assert lesson.id is not None
        assert lesson.title == "Introduction to Fractions"
        assert lesson.lesson_number == 1
        assert lesson.status == "draft"
        assert len(lesson.learning_objectives) == 2

    @pytest.mark.asyncio
    async def test_get_lesson_by_id(self, lesson_repository, sample_lesson_data):
        """Test retrieving a lesson by ID"""
        created_lesson = await lesson_repository.create(sample_lesson_data)
        retrieved_lesson = await lesson_repository.get_by_id(created_lesson.id)

        assert retrieved_lesson is not None
        assert retrieved_lesson.id == created_lesson.id
        assert retrieved_lesson.title == created_lesson.title

    @pytest.mark.asyncio
    async def test_get_lessons_by_school(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test retrieving lessons by school"""
        # Create multiple lessons
        await lesson_repository.create(sample_lesson_data)

        lesson_data_2 = sample_lesson_data.copy()
        lesson_data_2["lesson_number"] = 2
        lesson_data_2["title"] = "Fraction Operations"
        await lesson_repository.create(lesson_data_2)

        lessons, total = await lesson_repository.get_by_school(test_school.id)

        assert total == 2
        assert len(lessons) == 2

    @pytest.mark.asyncio
    async def test_get_lessons_by_class(
        self, lesson_repository, sample_lesson_data, test_class
    ):
        """Test retrieving lessons by class"""
        await lesson_repository.create(sample_lesson_data)

        lessons = await lesson_repository.get_by_class(test_class.id)

        assert len(lessons) == 1
        assert lessons[0].class_id == test_class.id

    @pytest.mark.asyncio
    async def test_get_lessons_by_teacher(
        self, lesson_repository, sample_lesson_data, test_school, test_teacher
    ):
        """Test retrieving lessons by teacher"""
        await lesson_repository.create(sample_lesson_data)

        lessons = await lesson_repository.get_by_teacher(
            test_school.id, test_teacher.id
        )

        assert len(lessons) == 1
        assert lessons[0].teacher_id == test_teacher.id

    @pytest.mark.asyncio
    async def test_get_lessons_by_date_range(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test retrieving lessons by date range"""
        await lesson_repository.create(sample_lesson_data)

        start_date = date.today()
        end_date = date.today() + timedelta(days=30)

        lessons = await lesson_repository.get_by_date_range(
            test_school.id, start_date, end_date
        )

        assert len(lessons) == 1

    @pytest.mark.asyncio
    async def test_get_upcoming_lessons(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test retrieving upcoming lessons"""
        await lesson_repository.create(sample_lesson_data)

        lessons = await lesson_repository.get_upcoming_lessons(
            test_school.id, days=30
        )

        assert len(lessons) == 1
        assert lessons[0].status in ['draft', 'scheduled']

    @pytest.mark.asyncio
    async def test_get_past_due_lessons(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test retrieving past due lessons"""
        # Create a past due lesson
        past_lesson_data = sample_lesson_data.copy()
        past_lesson_data["scheduled_date"] = date.today() - timedelta(days=7)
        past_lesson_data["status"] = "scheduled"
        await lesson_repository.create(past_lesson_data)

        lessons = await lesson_repository.get_past_due_lessons(test_school.id)

        assert len(lessons) == 1

    @pytest.mark.asyncio
    async def test_search_lessons(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test searching lessons"""
        await lesson_repository.create(sample_lesson_data)

        lessons, total = await lesson_repository.search(
            test_school.id, "fractions"
        )

        assert total == 1
        assert "fraction" in lessons[0].title.lower()

    @pytest.mark.asyncio
    async def test_get_templates(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test retrieving lesson templates"""
        template_data = sample_lesson_data.copy()
        template_data["is_template"] = True
        await lesson_repository.create(template_data)

        templates = await lesson_repository.get_templates(test_school.id)

        assert len(templates) == 1
        assert templates[0].is_template is True

    @pytest.mark.asyncio
    async def test_get_next_lesson_number(
        self, lesson_repository, sample_lesson_data, test_class
    ):
        """Test getting next lesson number"""
        await lesson_repository.create(sample_lesson_data)

        next_number = await lesson_repository.get_next_lesson_number(test_class.id)

        assert next_number == 2

    @pytest.mark.asyncio
    async def test_update_lesson(
        self, lesson_repository, sample_lesson_data
    ):
        """Test updating a lesson"""
        lesson = await lesson_repository.create(sample_lesson_data)

        updated_lesson = await lesson_repository.update(
            lesson.id, {"title": "Updated Title", "status": "scheduled"}
        )

        assert updated_lesson is not None
        assert updated_lesson.title == "Updated Title"
        assert updated_lesson.status == "scheduled"

    @pytest.mark.asyncio
    async def test_delete_lesson(
        self, lesson_repository, sample_lesson_data
    ):
        """Test soft deleting a lesson"""
        lesson = await lesson_repository.create(sample_lesson_data)

        success = await lesson_repository.delete(lesson.id)

        assert success is True

        # Verify it's soft deleted
        deleted_lesson = await lesson_repository.get_by_id(lesson.id)
        assert deleted_lesson is None

    @pytest.mark.asyncio
    async def test_lesson_number_exists(
        self, lesson_repository, sample_lesson_data, test_class
    ):
        """Test checking if lesson number exists"""
        await lesson_repository.create(sample_lesson_data)

        exists = await lesson_repository.lesson_number_exists(test_class.id, 1)
        assert exists is True

        exists = await lesson_repository.lesson_number_exists(test_class.id, 999)
        assert exists is False

    @pytest.mark.asyncio
    async def test_get_statistics(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test getting lesson statistics"""
        # Create lessons with different statuses
        await lesson_repository.create(sample_lesson_data)

        completed_data = sample_lesson_data.copy()
        completed_data["lesson_number"] = 2
        completed_data["status"] = "completed"
        completed_data["completion_percentage"] = 100
        await lesson_repository.create(completed_data)

        stats = await lesson_repository.get_statistics(school_id=test_school.id)

        assert stats["total_lessons"] == 2
        assert stats["by_status"]["draft"] == 1
        assert stats["by_status"]["completed"] == 1
        assert stats["completion_rate"] == 50.0

    @pytest.mark.asyncio
    async def test_filter_lessons_by_status(
        self, lesson_repository, sample_lesson_data, test_school
    ):
        """Test filtering lessons by status"""
        # Create draft lesson
        await lesson_repository.create(sample_lesson_data)

        # Create scheduled lesson
        scheduled_data = sample_lesson_data.copy()
        scheduled_data["lesson_number"] = 2
        scheduled_data["status"] = "scheduled"
        await lesson_repository.create(scheduled_data)

        # Filter by draft status
        lessons, total = await lesson_repository.get_by_school(
            test_school.id, status="draft"
        )

        assert total == 1
        assert lessons[0].status == "draft"

    @pytest.mark.asyncio
    async def test_count_by_class(
        self, lesson_repository, sample_lesson_data, test_class
    ):
        """Test counting lessons by class"""
        await lesson_repository.create(sample_lesson_data)

        count = await lesson_repository.count_by_class(test_class.id)

        assert count == 1

    @pytest.mark.asyncio
    async def test_count_by_teacher(
        self, lesson_repository, sample_lesson_data, test_school, test_teacher
    ):
        """Test counting lessons by teacher"""
        await lesson_repository.create(sample_lesson_data)

        count = await lesson_repository.count_by_teacher(
            test_teacher.id, test_school.id
        )

        assert count == 1
