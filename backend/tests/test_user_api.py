"""
User API Tests
Integration tests for User API endpoints
"""
import pytest
from httpx import AsyncClient
from main import app
from sqlalchemy.ext.asyncio import AsyncSession
import uuid


@pytest.fixture
async def test_client(test_session):
    """Create test HTTP client"""
    # Override the database dependency
    from config.database import get_db

    async def override_get_db():
        try:
            yield test_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestUserAPI:
    """Test suite for User API endpoints"""

    async def test_create_user(self, test_client, test_school):
        """Test POST /api/v1/users"""
        response = await test_client.post(
            "/api/v1/users",
            json={
                "email": "api@test.edu",
                "first_name": "API",
                "last_name": "Test",
                "persona": "teacher",
                "password": "TestPass123!",
                "school_id": str(test_school.id)
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "api@test.edu"
        assert data["full_name"] == "API Test"
        assert data["persona"] == "teacher"
        assert "id" in data

    async def test_create_user_duplicate_email(self, test_client, test_admin_user, test_school):
        """Test creating user with duplicate email"""
        response = await test_client.post(
            "/api/v1/users",
            json={
                "email": test_admin_user.email,
                "first_name": "Duplicate",
                "last_name": "User",
                "persona": "teacher",
                "password": "TestPass123!",
                "school_id": str(test_school.id)
            }
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_create_user_invalid_email(self, test_client, test_school):
        """Test creating user with invalid email"""
        response = await test_client.post(
            "/api/v1/users",
            json={
                "email": "invalid-email",
                "first_name": "Invalid",
                "last_name": "Email",
                "persona": "teacher",
                "password": "TestPass123!",
                "school_id": str(test_school.id)
            }
        )

        assert response.status_code == 422  # Validation error

    async def test_list_users(self, test_client, test_users):
        """Test GET /api/v1/users"""
        response = await test_client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 5
        assert data["pagination"]["total"] == 5

    async def test_list_users_with_filters(self, test_client, test_users):
        """Test listing users with filters"""
        response = await test_client.get(
            "/api/v1/users",
            params={"persona": "teacher", "limit": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["persona"] == "teacher"

    async def test_list_users_with_search(self, test_client, test_users):
        """Test listing users with search"""
        response = await test_client.get(
            "/api/v1/users",
            params={"search": "Administrator"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1

    async def test_list_users_pagination(self, test_client, test_users):
        """Test user list pagination"""
        response = await test_client.get(
            "/api/v1/users",
            params={"page": 1, "limit": 2}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["pages"] == 3

    async def test_get_user(self, test_client, test_admin_user):
        """Test GET /api/v1/users/{id}"""
        response = await test_client.get(f"/api/v1/users/{test_admin_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_admin_user.id)
        assert data["email"] == test_admin_user.email

    async def test_get_user_not_found(self, test_client):
        """Test getting non-existent user"""
        random_id = uuid.uuid4()
        response = await test_client.get(f"/api/v1/users/{random_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_user(self, test_client, test_teacher_user):
        """Test PUT /api/v1/users/{id}"""
        response = await test_client.put(
            f"/api/v1/users/{test_teacher_user.id}",
            json={
                "first_name": "Updated",
                "last_name": "Teacher"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Teacher"
        assert data["full_name"] == "Updated Teacher"

    async def test_update_user_not_found(self, test_client):
        """Test updating non-existent user"""
        random_id = uuid.uuid4()
        response = await test_client.put(
            f"/api/v1/users/{random_id}",
            json={"first_name": "Updated"}
        )

        assert response.status_code == 404

    async def test_delete_user(self, test_client, test_student_user):
        """Test DELETE /api/v1/users/{id}"""
        response = await test_client.delete(f"/api/v1/users/{test_student_user.id}")

        assert response.status_code == 204

        # Verify user is soft deleted
        get_response = await test_client.get(f"/api/v1/users/{test_student_user.id}")
        assert get_response.status_code == 404

    async def test_delete_user_not_found(self, test_client):
        """Test deleting non-existent user"""
        random_id = uuid.uuid4()
        response = await test_client.delete(f"/api/v1/users/{random_id}")

        assert response.status_code == 404

    async def test_change_user_status(self, test_client, test_teacher_user):
        """Test PATCH /api/v1/users/{id}/status"""
        response = await test_client.patch(
            f"/api/v1/users/{test_teacher_user.id}/status",
            json={"status": "suspended"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "suspended"
        assert data["is_active"] is False

    async def test_change_user_status_invalid(self, test_client, test_teacher_user):
        """Test changing to invalid status"""
        response = await test_client.patch(
            f"/api/v1/users/{test_teacher_user.id}/status",
            json={"status": "invalid"}
        )

        assert response.status_code == 422  # Validation error

    async def test_change_user_persona(self, test_client, test_student_user):
        """Test PATCH /api/v1/users/{id}/persona"""
        response = await test_client.patch(
            f"/api/v1/users/{test_student_user.id}/persona",
            json={"persona": "parent"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["persona"] == "parent"

    async def test_change_user_persona_invalid(self, test_client, test_student_user):
        """Test changing to invalid persona"""
        response = await test_client.patch(
            f"/api/v1/users/{test_student_user.id}/persona",
            json={"persona": "invalid"}
        )

        assert response.status_code == 422  # Validation error

    async def test_get_statistics(self, test_client, test_users):
        """Test GET /api/v1/users/statistics/summary"""
        response = await test_client.get("/api/v1/users/statistics/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert "by_persona" in data
        assert "by_status" in data
        assert data["by_persona"]["administrators"] == 1
        assert data["by_status"]["active"] == 5

    async def test_api_validation_error(self, test_client, test_school):
        """Test API validation with missing required fields"""
        response = await test_client.post(
            "/api/v1/users",
            json={
                "email": "incomplete@test.edu"
                # Missing required fields
            }
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert isinstance(detail, list)
        assert len(detail) > 0

    async def test_api_weak_password(self, test_client, test_school):
        """Test API validation with weak password"""
        response = await test_client.post(
            "/api/v1/users",
            json={
                "email": "weak@test.edu",
                "first_name": "Weak",
                "last_name": "Password",
                "persona": "teacher",
                "password": "weak",  # Too weak
                "school_id": str(test_school.id)
            }
        )

        assert response.status_code == 422
