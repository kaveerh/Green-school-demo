"""
API Client

HTTP client for Green School Management System API with retry logic.
"""
import requests
import time
import logging
from typing import Dict, List, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class SchoolAPIClient:
    """
    HTTP client for Green School Management System API

    Features:
    - Automatic retry with exponential backoff
    - Request/response logging
    - Error handling and reporting
    - Support for all 15 API endpoints
    """

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize API client

        Args:
            base_url: Base URL of the API (e.g., http://localhost:8000)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Default headers
        self.session.headers.update({"Content-Type": "application/json"})

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Any:
        """
        Make HTTP request with error handling

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            requests.exceptions.HTTPError: On HTTP error
        """
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"{method} {url}")
        if data:
            logger.debug(f"Request data: {data}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            # Return JSON if response has content
            if response.content:
                return response.json()
            return None

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Response: {error_detail}")
                except:
                    logger.error(f"Response: {e.response.text}")
            else:
                logger.error(f"Response: No response")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
            raise

    # Generic CRUD operations
    def create(self, endpoint: str, data: Dict) -> Dict:
        """POST request to create entity"""
        return self._request("POST", endpoint, data=data)

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET request"""
        return self._request("GET", endpoint, params=params)

    def update(self, endpoint: str, entity_id: str, data: Dict) -> Dict:
        """PUT request to update entity"""
        return self._request("PUT", f"{endpoint}/{entity_id}", data=data)

    def delete(self, endpoint: str, entity_id: str) -> None:
        """DELETE request"""
        self._request("DELETE", f"{endpoint}/{entity_id}")

    # School API
    def create_school(self, data: Dict) -> Dict:
        """Create school"""
        return self.create("/api/v1/schools", data)

    def get_school(self, school_id: str) -> Dict:
        """Get school by ID"""
        return self.get(f"/api/v1/schools/{school_id}")

    # User API
    def create_user(self, data: Dict) -> Dict:
        """Create user"""
        return self.create("/api/v1/users", data)

    def list_users(self, school_id: str, **filters) -> List[Dict]:
        """List users with filters"""
        params = {"school_id": school_id, **filters}
        response = self.get("/api/v1/users", params=params)
        return response.get("data", [])

    # Teacher API
    def create_teacher(self, data: Dict) -> Dict:
        """Create teacher"""
        return self.create("/api/v1/teachers", data)

    def list_teachers(self, school_id: str, **filters) -> List[Dict]:
        """List teachers"""
        params = {"school_id": school_id, **filters}
        response = self.get("/api/v1/teachers", params=params)
        return response.get("data", [])

    # Parent API
    def create_parent(self, data: Dict) -> Dict:
        """Create parent"""
        return self.create("/api/v1/parents", data)

    def list_parents(self, school_id: str, **filters) -> List[Dict]:
        """List parents"""
        params = {"school_id": school_id, **filters}
        response = self.get("/api/v1/parents", params=params)
        return response.get("data", [])

    # Student API
    def create_student(self, data: Dict) -> Dict:
        """Create student"""
        return self.create("/api/v1/students", data)

    def list_students(self, school_id: str, **filters) -> List[Dict]:
        """List students"""
        params = {"school_id": school_id, **filters}
        response = self.get("/api/v1/students", params=params)
        return response.get("data", [])

    # Parent-Student Relationship API
    def create_parent_student_relationship(self, data: Dict) -> Dict:
        """Create parent-student relationship"""
        return self.create("/api/v1/parents/student-relationships", data)

    # Subject API
    def create_subject(self, data: Dict) -> Dict:
        """Create subject"""
        return self.create("/api/v1/subjects", data)

    def list_subjects(self, school_id: str) -> List[Dict]:
        """List subjects"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/subjects", params=params)
        return response.get("data", [])

    # Room API
    def create_room(self, data: Dict) -> Dict:
        """Create room"""
        return self.create("/api/v1/rooms", data)

    def list_rooms(self, school_id: str) -> List[Dict]:
        """List rooms"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/rooms", params=params)
        return response.get("data", [])

    # Class API
    def create_class(self, data: Dict) -> Dict:
        """Create class"""
        return self.create("/api/v1/classes", data)

    def enroll_student_in_class(self, class_id: str, data: Dict) -> Dict:
        """Enroll student in class"""
        return self.create(f"/api/v1/classes/{class_id}/students", data)

    def list_classes(self, school_id: str) -> List[Dict]:
        """List classes"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/classes", params=params)
        return response.get("data", [])

    # Lesson API
    def create_lesson(self, data: Dict) -> Dict:
        """Create lesson"""
        return self.create("/api/v1/lessons", data)

    def list_lessons(self, school_id: str) -> List[Dict]:
        """List lessons"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/lessons", params=params)
        return response.get("data", [])

    # Assessment API
    def create_assessment(self, data: Dict) -> Dict:
        """Create assessment"""
        return self.create("/api/v1/assessments", data)

    def list_assessments(self, school_id: str) -> List[Dict]:
        """List assessments"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/assessments", params=params)
        return response.get("data", [])

    # Attendance API
    def create_attendance(self, data: Dict) -> Dict:
        """Create single attendance record"""
        return self.create("/api/v1/attendance", data)

    def bulk_create_attendance(self, data: Dict) -> List[Dict]:
        """Bulk create attendance records"""
        return self.create("/api/v1/attendance/bulk", data)

    def list_attendance(self, school_id: str) -> List[Dict]:
        """List attendance records"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/attendance", params=params)
        return response.get("data", [])

    # Event API
    def create_event(self, data: Dict) -> Dict:
        """Create event"""
        # Extract created_by_id for query parameter
        created_by_id = data.pop("created_by_id", None)
        if not created_by_id:
            # Use organizer_id as fallback
            created_by_id = data.get("organizer_id")
        
        params = {"created_by_id": created_by_id} if created_by_id else {}
        return self._request("POST", "/api/v1/events", data=data, params=params)

    def list_events(self, school_id: str) -> List[Dict]:
        """List events"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/events", params=params)
        return response.get("data", [])

    # Activity API
    def create_activity(self, data: Dict) -> Dict:
        """Create activity"""
        return self.create("/api/v1/activities", data)

    def list_activities(self, school_id: str) -> List[Dict]:
        """List activities"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/activities", params=params)
        return response.get("data", [])

    # Vendor API
    def create_vendor(self, data: Dict) -> Dict:
        """Create vendor"""
        # Extract created_by_id for query parameter
        created_by_id = data.pop("created_by_id", None)
        if not created_by_id:
            # Use first admin user as fallback
            # This should be set by the generator
            raise ValueError("created_by_id is required for vendor creation")
        
        params = {"created_by_id": created_by_id}
        return self._request("POST", "/api/v1/vendors", data=data, params=params)

    def list_vendors(self, school_id: str) -> List[Dict]:
        """List vendors"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/vendors", params=params)
        return response.get("data", [])

    # Merit API
    def create_merit(self, data: Dict) -> Dict:
        """Create merit"""
        return self.create("/api/v1/merits", data)

    def list_merits(self, school_id: str) -> List[Dict]:
        """List merits"""
        params = {"school_id": school_id}
        response = self.get("/api/v1/merits", params=params)
        return response.get("data", [])
