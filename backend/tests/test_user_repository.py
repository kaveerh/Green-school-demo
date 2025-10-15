"""
User Repository Tests
Test cases for UserRepository data access layer
"""
import pytest
from repositories.user_repository import UserRepository
from models import User


@pytest.mark.asyncio
class TestUserRepository:
    """Test suite for UserRepository"""

    async def test_create_user(self, test_session, test_school):
        """Test creating a user"""
        repo = UserRepository(test_session)

        user_data = {
            "school_id": test_school.id,
            "email": "new@test.edu",
            "first_name": "New",
            "last_name": "User",
            "persona": "teacher",
            "status": "active"
        }

        user = await repo.create(user_data)
        await test_session.commit()

        assert user.id is not None
        assert user.email == "new@test.edu"
        assert user.first_name == "New"
        assert user.persona == "teacher"
        assert user.school_id == test_school.id

    async def test_find_by_id(self, test_session, test_admin_user):
        """Test finding user by ID"""
        repo = UserRepository(test_session)

        user = await repo.find_by_id(test_admin_user.id)

        assert user is not None
        assert user.id == test_admin_user.id
        assert user.email == test_admin_user.email

    async def test_find_by_id_not_found(self, test_session):
        """Test finding non-existent user"""
        repo = UserRepository(test_session)

        from uuid import uuid4
        user = await repo.find_by_id(uuid4())

        assert user is None

    async def test_find_by_email(self, test_session, test_admin_user, test_school):
        """Test finding user by email"""
        repo = UserRepository(test_session)

        user = await repo.find_by_email(test_admin_user.email, test_school.id)

        assert user is not None
        assert user.email == test_admin_user.email
        assert user.id == test_admin_user.id

    async def test_find_by_email_not_found(self, test_session, test_school):
        """Test finding non-existent email"""
        repo = UserRepository(test_session)

        user = await repo.find_by_email("nonexistent@test.edu", test_school.id)

        assert user is None

    async def test_find_all_with_pagination(self, test_session, test_users):
        """Test finding all users with pagination"""
        repo = UserRepository(test_session)

        users, total = await repo.find_all(page=1, limit=3)

        assert len(users) == 3
        assert total == 5

    async def test_find_all_with_filters(self, test_session, test_users):
        """Test finding users with filters"""
        repo = UserRepository(test_session)

        users, total = await repo.find_all(filters={"persona": "teacher"})

        assert len(users) == 1
        assert total == 1
        assert users[0].persona == "teacher"

    async def test_update_user(self, test_session, test_admin_user):
        """Test updating a user"""
        repo = UserRepository(test_session)

        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }

        user = await repo.update(test_admin_user.id, update_data)
        await test_session.commit()

        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.email == test_admin_user.email  # Unchanged

    async def test_delete_user_soft(self, test_session, test_admin_user):
        """Test soft deleting a user"""
        repo = UserRepository(test_session)

        success = await repo.delete(test_admin_user.id)
        await test_session.commit()

        assert success is True

        # Verify soft delete
        user = await repo.find_by_id(test_admin_user.id, include_deleted=True)
        assert user is not None
        assert user.deleted_at is not None

        # Verify not found without include_deleted
        user = await repo.find_by_id(test_admin_user.id)
        assert user is None

    async def test_search_users(self, test_session, test_users, test_school):
        """Test searching users"""
        repo = UserRepository(test_session)

        # Search by name
        users, total = await repo.search_users(
            school_id=test_school.id,
            search_term="Teacher"
        )

        assert len(users) >= 1
        assert any("Teacher" in user.first_name for user in users)

    async def test_search_users_with_filters(self, test_session, test_users, test_school):
        """Test searching users with persona filter"""
        repo = UserRepository(test_session)

        users, total = await repo.search_users(
            school_id=test_school.id,
            persona="student"
        )

        assert len(users) == 1
        assert users[0].persona == "student"

    async def test_count_by_persona(self, test_session, test_users, test_school):
        """Test counting users by persona"""
        repo = UserRepository(test_session)

        count = await repo.count_by_persona(test_school.id, "teacher")

        assert count == 1

    async def test_count_by_status(self, test_session, test_users, test_school):
        """Test counting users by status"""
        repo = UserRepository(test_session)

        count = await repo.count_by_status(test_school.id, "active")

        assert count == 5  # All test users are active

    async def test_get_statistics(self, test_session, test_users, test_school):
        """Test getting user statistics"""
        repo = UserRepository(test_session)

        stats = await repo.get_statistics(test_school.id)

        assert stats["total"] == 5
        assert stats["by_persona"]["administrators"] == 1
        assert stats["by_persona"]["teachers"] == 1
        assert stats["by_persona"]["students"] == 1
        assert stats["by_status"]["active"] == 5

    async def test_email_exists(self, test_session, test_admin_user):
        """Test checking if email exists"""
        repo = UserRepository(test_session)

        exists = await repo.email_exists(test_admin_user.email)
        assert exists is True

        exists = await repo.email_exists("nonexistent@test.edu")
        assert exists is False

    async def test_email_exists_exclude_id(self, test_session, test_admin_user):
        """Test email exists excluding specific user ID"""
        repo = UserRepository(test_session)

        # Should return False when excluding the user with that email
        exists = await repo.email_exists(
            test_admin_user.email,
            exclude_id=test_admin_user.id
        )
        assert exists is False

    async def test_update_last_login(self, test_session, test_admin_user):
        """Test updating last login timestamp"""
        repo = UserRepository(test_session)

        assert test_admin_user.last_login is None

        user = await repo.update_last_login(test_admin_user.id)
        await test_session.commit()

        assert user.last_login is not None

    async def test_change_status(self, test_session, test_admin_user):
        """Test changing user status"""
        repo = UserRepository(test_session)

        user = await repo.change_status(test_admin_user.id, "inactive")
        await test_session.commit()

        assert user.status == "inactive"

    async def test_change_status_invalid(self, test_session, test_admin_user):
        """Test changing to invalid status"""
        repo = UserRepository(test_session)

        with pytest.raises(ValueError):
            await repo.change_status(test_admin_user.id, "invalid_status")

    async def test_change_persona(self, test_session, test_teacher_user):
        """Test changing user persona"""
        repo = UserRepository(test_session)

        user = await repo.change_persona(test_teacher_user.id, "administrator")
        await test_session.commit()

        assert user.persona == "administrator"

    async def test_change_persona_invalid(self, test_session, test_teacher_user):
        """Test changing to invalid persona"""
        repo = UserRepository(test_session)

        with pytest.raises(ValueError):
            await repo.change_persona(test_teacher_user.id, "invalid_persona")

    async def test_find_by_school(self, test_session, test_users, test_school):
        """Test finding users by school"""
        repo = UserRepository(test_session)

        users, total = await repo.find_by_school(test_school.id)

        assert total == 5
        assert all(user.school_id == test_school.id for user in users)

    async def test_find_by_school_with_persona_filter(self, test_session, test_users, test_school):
        """Test finding users by school with persona filter"""
        repo = UserRepository(test_session)

        users, total = await repo.find_by_school(
            test_school.id,
            persona="parent"
        )

        assert total == 1
        assert users[0].persona == "parent"

    async def test_find_by_keycloak_id(self, test_session, test_school):
        """Test finding user by Keycloak ID"""
        repo = UserRepository(test_session)

        # Create user with Keycloak ID
        user_data = {
            "school_id": test_school.id,
            "email": "keycloak@test.edu",
            "first_name": "Keycloak",
            "last_name": "User",
            "persona": "teacher",
            "keycloak_id": "kc-123-456"
        }
        created = await repo.create(user_data)
        await test_session.commit()

        # Find by Keycloak ID
        found = await repo.find_by_keycloak_id("kc-123-456")

        assert found is not None
        assert found.id == created.id
        assert found.keycloak_id == "kc-123-456"
