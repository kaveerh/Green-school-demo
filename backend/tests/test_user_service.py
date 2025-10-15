"""
User Service Tests
Test cases for UserService business logic layer
"""
import pytest
from services.user_service import UserService
from schemas.user_schema import (
    UserCreateSchema,
    UserUpdateSchema,
    UserSearchSchema,
    PersonaEnum,
    StatusEnum
)


@pytest.mark.asyncio
class TestUserService:
    """Test suite for UserService"""

    async def test_create_user(self, test_session, test_school, test_admin_user):
        """Test creating a user"""
        service = UserService(test_session)

        user_data = UserCreateSchema(
            email="newuser@test.edu",
            first_name="New",
            last_name="User",
            persona=PersonaEnum.TEACHER,
            password="TestPass123!",
            school_id=test_school.id
        )

        user = await service.create_user(user_data, test_admin_user.id)

        assert user.email == "newuser@test.edu"
        assert user.full_name == "New User"
        assert user.persona == PersonaEnum.TEACHER
        # Password should be hashed, not plain
        assert user.id is not None

    async def test_create_user_duplicate_email(self, test_session, test_school, test_admin_user):
        """Test creating user with duplicate email"""
        service = UserService(test_session)

        user_data = UserCreateSchema(
            email=test_admin_user.email,  # Duplicate
            first_name="Duplicate",
            last_name="User",
            persona=PersonaEnum.TEACHER,
            password="TestPass123!",
            school_id=test_school.id
        )

        with pytest.raises(ValueError, match="already exists"):
            await service.create_user(user_data, test_admin_user.id)

    async def test_get_user(self, test_session, test_admin_user):
        """Test getting a user"""
        service = UserService(test_session)

        user = await service.get_user(
            test_admin_user.id,
            requesting_user_id=test_admin_user.id,
            requesting_user_persona="administrator"
        )

        assert user is not None
        assert user.id == test_admin_user.id
        assert user.email == test_admin_user.email

    async def test_get_user_permission_denied(self, test_session, test_admin_user, test_teacher_user):
        """Test getting another user without permission"""
        service = UserService(test_session)

        with pytest.raises(PermissionError):
            await service.get_user(
                test_admin_user.id,
                requesting_user_id=test_teacher_user.id,
                requesting_user_persona="teacher"
            )

    async def test_get_user_self(self, test_session, test_teacher_user):
        """Test user getting their own profile"""
        service = UserService(test_session)

        user = await service.get_user(
            test_teacher_user.id,
            requesting_user_id=test_teacher_user.id,
            requesting_user_persona="teacher"
        )

        assert user is not None
        assert user.id == test_teacher_user.id

    async def test_get_user_by_email(self, test_session, test_admin_user, test_school):
        """Test getting user by email"""
        service = UserService(test_session)

        user = await service.get_user_by_email(test_admin_user.email, test_school.id)

        assert user is not None
        assert user.email == test_admin_user.email

    async def test_search_users(self, test_session, test_users, test_school):
        """Test searching users"""
        service = UserService(test_session)

        search_params = UserSearchSchema(page=1, limit=10)

        users, pagination = await service.search_users(
            school_id=test_school.id,
            search_params=search_params,
            requesting_user_persona="administrator"
        )

        assert len(users) == 5
        assert pagination["total"] == 5
        assert pagination["pages"] == 1

    async def test_search_users_with_filters(self, test_session, test_users, test_school):
        """Test searching users with filters"""
        service = UserService(test_session)

        search_params = UserSearchSchema(
            persona=PersonaEnum.TEACHER,
            page=1,
            limit=10
        )

        users, pagination = await service.search_users(
            school_id=test_school.id,
            search_params=search_params,
            requesting_user_persona="administrator"
        )

        assert len(users) == 1
        assert users[0].persona == PersonaEnum.TEACHER

    async def test_search_users_permission_denied(self, test_session, test_school):
        """Test searching users without admin permission"""
        service = UserService(test_session)

        search_params = UserSearchSchema()

        with pytest.raises(PermissionError):
            await service.search_users(
                school_id=test_school.id,
                search_params=search_params,
                requesting_user_persona="teacher"
            )

    async def test_update_user(self, test_session, test_admin_user):
        """Test updating a user"""
        service = UserService(test_session)

        update_data = UserUpdateSchema(
            first_name="Updated",
            last_name="Name"
        )

        user = await service.update_user(
            test_admin_user.id,
            update_data,
            updated_by_id=test_admin_user.id,
            requesting_user_persona="administrator"
        )

        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.full_name == "Updated Name"

    async def test_update_user_permission_denied(self, test_session, test_admin_user, test_teacher_user):
        """Test updating another user without permission"""
        service = UserService(test_session)

        update_data = UserUpdateSchema(first_name="Hacked")

        with pytest.raises(PermissionError):
            await service.update_user(
                test_admin_user.id,
                update_data,
                updated_by_id=test_teacher_user.id,
                requesting_user_persona="teacher"
            )

    async def test_delete_user(self, test_session, test_teacher_user, test_admin_user):
        """Test deleting a user"""
        service = UserService(test_session)

        success = await service.delete_user(
            test_teacher_user.id,
            deleted_by_id=test_admin_user.id,
            requesting_user_persona="administrator"
        )

        assert success is True

    async def test_delete_user_permission_denied(self, test_session, test_teacher_user):
        """Test deleting user without admin permission"""
        service = UserService(test_session)

        with pytest.raises(PermissionError):
            await service.delete_user(
                test_teacher_user.id,
                deleted_by_id=test_teacher_user.id,
                requesting_user_persona="teacher"
            )

    async def test_change_user_status(self, test_session, test_teacher_user, test_admin_user):
        """Test changing user status"""
        service = UserService(test_session)

        user = await service.change_user_status(
            test_teacher_user.id,
            "inactive",
            updated_by_id=test_admin_user.id,
            requesting_user_persona="administrator"
        )

        assert user.status == StatusEnum.INACTIVE
        assert user.is_active is False

    async def test_change_user_status_permission_denied(self, test_session, test_teacher_user):
        """Test changing status without admin permission"""
        service = UserService(test_session)

        with pytest.raises(PermissionError):
            await service.change_user_status(
                test_teacher_user.id,
                "inactive",
                updated_by_id=test_teacher_user.id,
                requesting_user_persona="teacher"
            )

    async def test_change_user_persona(self, test_session, test_teacher_user, test_admin_user):
        """Test changing user persona"""
        service = UserService(test_session)

        user = await service.change_user_persona(
            test_teacher_user.id,
            "student",
            updated_by_id=test_admin_user.id,
            requesting_user_persona="administrator"
        )

        assert user.persona == PersonaEnum.STUDENT

    async def test_change_user_persona_permission_denied(self, test_session, test_teacher_user):
        """Test changing persona without admin permission"""
        service = UserService(test_session)

        with pytest.raises(PermissionError):
            await service.change_user_persona(
                test_teacher_user.id,
                "administrator",
                updated_by_id=test_teacher_user.id,
                requesting_user_persona="teacher"
            )

    async def test_get_statistics(self, test_session, test_users, test_school):
        """Test getting user statistics"""
        service = UserService(test_session)

        stats = await service.get_statistics(
            test_school.id,
            requesting_user_persona="administrator"
        )

        assert stats.total == 5
        assert stats.by_persona["administrators"] == 1
        assert stats.by_persona["teachers"] == 1
        assert stats.by_status["active"] == 5

    async def test_get_statistics_permission_denied(self, test_session, test_school):
        """Test getting statistics without admin permission"""
        service = UserService(test_session)

        with pytest.raises(PermissionError):
            await service.get_statistics(
                test_school.id,
                requesting_user_persona="teacher"
            )

    async def test_verify_password(self, test_session, test_school, test_admin_user):
        """Test password verification"""
        service = UserService(test_session)

        # First create a user with password
        from utils.security import hash_password
        from repositories.user_repository import UserRepository

        repo = UserRepository(test_session)
        password = "TestPass123!"
        hashed = hash_password(password)

        user_data = {
            "school_id": test_school.id,
            "email": "password@test.edu",
            "first_name": "Password",
            "last_name": "Test",
            "persona": "teacher",
            "password_hash": hashed
        }
        user = await repo.create(user_data)
        await test_session.commit()

        # Verify correct password
        result = await service.verify_password(user.id, password)
        assert result is True

        # Verify incorrect password
        result = await service.verify_password(user.id, "WrongPass123!")
        assert result is False

    async def test_update_last_login(self, test_session, test_admin_user):
        """Test updating last login"""
        service = UserService(test_session)

        user = await service.update_last_login(test_admin_user.id)

        assert user is not None
        assert user.last_login is not None
