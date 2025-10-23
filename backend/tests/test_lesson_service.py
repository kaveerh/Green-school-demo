"""
Lesson Service Tests

Unit tests for LessonService business logic
"""
import pytest
from datetime import date, timedelta
import uuid

from services.lesson_service import LessonService
from repositories.lesson_repository import LessonRepository
from repositories.teacher_repository import TeacherRepository
from repositories.class_repository import ClassRepository
from repositories.subject_repository import SubjectRepository
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
async def lesson_service(test_session):
    """Create a lesson service instance"""
    lesson_repo = LessonRepository(test_session)
    teacher_repo = TeacherRepository(test_session)
    class_repo = ClassRepository(test_session)
    subject_repo = SubjectRepository(test_session)
    return LessonService(lesson_repo, teacher_repo, class_repo, subject_repo)


class TestLessonService:
    """Test suite for LessonService"""

    @pytest.mark.asyncio
    async def test_create_lesson(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test creating a lesson with validation"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Introduction to Fractions",
            scheduled_date=date.today() + timedelta(days=7),
            duration_minutes=45,
            learning_objectives=["Understand fractions"],
            materials_needed=["Fraction strips"]
        )

        assert lesson is not None
        assert lesson.title == "Introduction to Fractions"
        assert lesson.lesson_number == 1
        assert lesson.status == "draft"

    @pytest.mark.asyncio
    async def test_create_lesson_invalid_title(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test creating a lesson with invalid title"""
        with pytest.raises(ValueError, match="Title must be between"):
            await lesson_service.create_lesson(
                school_id=test_school.id,
                class_id=test_class.id,
                teacher_id=test_teacher.id,
                subject_id=test_subject.id,
                title="",  # Invalid: empty title
                scheduled_date=date.today(),
                duration_minutes=45
            )

    @pytest.mark.asyncio
    async def test_create_lesson_invalid_duration(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test creating a lesson with invalid duration"""
        with pytest.raises(ValueError, match="Duration must be between"):
            await lesson_service.create_lesson(
                school_id=test_school.id,
                class_id=test_class.id,
                teacher_id=test_teacher.id,
                subject_id=test_subject.id,
                title="Test Lesson",
                scheduled_date=date.today(),
                duration_minutes=500  # Invalid: too long
            )

    @pytest.mark.asyncio
    async def test_create_lesson_invalid_teacher(
        self, lesson_service, test_school, test_class, test_subject
    ):
        """Test creating a lesson with non-existent teacher"""
        with pytest.raises(ValueError, match="Teacher .* not found"):
            await lesson_service.create_lesson(
                school_id=test_school.id,
                class_id=test_class.id,
                teacher_id=uuid.uuid4(),  # Non-existent teacher
                subject_id=test_subject.id,
                title="Test Lesson",
                scheduled_date=date.today(),
                duration_minutes=45
            )

    @pytest.mark.asyncio
    async def test_auto_increment_lesson_number(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test automatic lesson number increment"""
        # Create first lesson
        lesson1 = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Lesson 1",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        # Create second lesson
        lesson2 = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Lesson 2",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        assert lesson1.lesson_number == 1
        assert lesson2.lesson_number == 2

    @pytest.mark.asyncio
    async def test_start_lesson(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test starting a lesson"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Test Lesson",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        started_lesson = await lesson_service.start_lesson(lesson.id)

        assert started_lesson.status == "in_progress"

    @pytest.mark.asyncio
    async def test_complete_lesson(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test completing a lesson"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Test Lesson",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        # Start the lesson first
        await lesson_service.start_lesson(lesson.id)

        # Complete the lesson
        completed_lesson = await lesson_service.complete_lesson(
            lesson.id,
            completion_percentage=100,
            actual_duration_minutes=50,
            what_went_well="Students engaged well",
            what_to_improve="Need more examples"
        )

        assert completed_lesson.status == "completed"
        assert completed_lesson.completion_percentage == 100
        assert completed_lesson.actual_duration_minutes == 50
        assert completed_lesson.what_went_well == "Students engaged well"

    @pytest.mark.asyncio
    async def test_complete_lesson_invalid_percentage(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test completing a lesson with invalid percentage"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Test Lesson",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        await lesson_service.start_lesson(lesson.id)

        with pytest.raises(ValueError, match="Completion percentage must be"):
            await lesson_service.complete_lesson(
                lesson.id,
                completion_percentage=150  # Invalid: > 100
            )

    @pytest.mark.asyncio
    async def test_cancel_lesson(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test cancelling a lesson"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Test Lesson",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        cancelled_lesson = await lesson_service.cancel_lesson(lesson.id)

        assert cancelled_lesson.status == "cancelled"

    @pytest.mark.asyncio
    async def test_update_lesson(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test updating a lesson"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Original Title",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        updated_lesson = await lesson_service.update_lesson(
            lesson.id,
            {"title": "Updated Title", "duration_minutes": 60}
        )

        assert updated_lesson.title == "Updated Title"
        assert updated_lesson.duration_minutes == 60

    @pytest.mark.asyncio
    async def test_convert_to_template(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test converting a lesson to a template"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Template Lesson",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        template = await lesson_service.convert_to_template(lesson.id)

        assert template.is_template is True

    @pytest.mark.asyncio
    async def test_duplicate_lesson(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test duplicating a lesson"""
        original = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Original Lesson",
            scheduled_date=date.today(),
            duration_minutes=45,
            learning_objectives=["Objective 1"]
        )

        duplicate = await lesson_service.duplicate_lesson(
            original.id,
            new_scheduled_date=date.today() + timedelta(days=7)
        )

        assert duplicate.id != original.id
        assert duplicate.title == original.title
        assert duplicate.lesson_number == 2
        assert duplicate.status == "draft"
        assert len(duplicate.learning_objectives) == 1

    @pytest.mark.asyncio
    async def test_delete_lesson(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test deleting a lesson"""
        lesson = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Test Lesson",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        await lesson_service.delete_lesson(lesson.id)

        # Verify it's deleted
        deleted_lesson = await lesson_service.get_lesson(lesson.id)
        assert deleted_lesson is None

    @pytest.mark.asyncio
    async def test_validate_color_format(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test color format validation"""
        with pytest.raises(ValueError, match="Color must be in format"):
            await lesson_service.create_lesson(
                school_id=test_school.id,
                class_id=test_class.id,
                teacher_id=test_teacher.id,
                subject_id=test_subject.id,
                title="Test Lesson",
                scheduled_date=date.today(),
                duration_minutes=45,
                color="invalid"  # Invalid color format
            )

    @pytest.mark.asyncio
    async def test_get_statistics(
        self, lesson_service, test_school, test_class, test_teacher, test_subject
    ):
        """Test getting lesson statistics"""
        # Create multiple lessons
        await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Draft Lesson",
            scheduled_date=date.today(),
            duration_minutes=45
        )

        lesson2 = await lesson_service.create_lesson(
            school_id=test_school.id,
            class_id=test_class.id,
            teacher_id=test_teacher.id,
            subject_id=test_subject.id,
            title="Completed Lesson",
            scheduled_date=date.today(),
            duration_minutes=50
        )
        await lesson_service.start_lesson(lesson2.id)
        await lesson_service.complete_lesson(lesson2.id, completion_percentage=100)

        stats = await lesson_service.get_statistics(school_id=test_school.id)

        assert stats["total_lessons"] == 2
        assert stats["by_status"]["draft"] == 1
        assert stats["by_status"]["completed"] == 1
        assert stats["completion_rate"] == 50.0
