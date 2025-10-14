# API Routes Master Documentation
**Version**: 1.0
**Last Updated**: 2025-10-13
**Base URL**: http://localhost:8000/api/v1

## Overview
Complete reference of all API routes for the Green School Management System. All routes require authentication via Keycloak unless marked as public.

## Authentication
- **Method**: Keycloak Bearer Token
- **Header**: `Authorization: Bearer {token}`
- **Keycloak Config**: http://localhost:8080/realms/Green-School-id/.well-known/openid-configuration
- **Test User**: admin@greenschool.edu / Password123

## Global Headers
```
Authorization: Bearer {token}
Content-Type: application/json
X-School-ID: {school_uuid}  // Multi-tenant isolation
```

## Common Response Codes
- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource
- `422 Unprocessable Entity` - Business logic error
- `500 Internal Server Error` - Server error

## Pagination Format
All list endpoints support pagination:
```
GET /api/v1/{resource}?page=1&limit=20&sort=created_at&order=desc
```

Response format:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Feature 01: Users

### Base Path: `/api/v1/users`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/users` | Create user | Required | Admin |
| GET | `/users` | List all users | Required | Admin |
| GET | `/users/{id}` | Get user details | Required | Admin/Self |
| PUT | `/users/{id}` | Update user | Required | Admin/Self |
| DELETE | `/users/{id}` | Delete user | Required | Admin |
| POST | `/users/{id}/verify-email` | Send verification email | Required | Admin/Self |
| POST | `/users/request-password-reset` | Request password reset | Public | - |
| POST | `/users/reset-password` | Reset password | Public | - |
| PATCH | `/users/{id}/change-persona` | Change user role | Required | Admin |
| PATCH | `/users/{id}/change-status` | Change user status | Required | Admin |

### Query Parameters (GET /users)
- `persona` - Filter by persona (administrator, teacher, student, parent, vendor)
- `status` - Filter by status (active, inactive, suspended)
- `search` - Search by name or email
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20, max: 100)

### Example Request
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -H "X-School-ID: {school_id}" \
  -d '{
    "email": "teacher@school.edu",
    "first_name": "John",
    "last_name": "Smith",
    "persona": "teacher",
    "password": "SecurePass123"
  }'
```

---

## Feature 02: Schools

### Base Path: `/api/v1/schools`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/schools` | Create school | Required | System Admin |
| GET | `/schools` | List all schools | Required | System Admin |
| GET | `/schools/{id}` | Get school details | Required | Admin |
| PUT | `/schools/{id}` | Update school | Required | Admin |
| DELETE | `/schools/{id}` | Delete school | Required | System Admin |
| POST | `/schools/{id}/upload-logo` | Upload school logo | Required | Admin |
| GET | `/schools/{id}/settings` | Get school settings | Required | Admin |
| PUT | `/schools/{id}/settings` | Update settings | Required | Admin |
| GET | `/schools/{id}/statistics` | Get school stats | Required | Admin |

---

## Feature 03: Teachers

### Base Path: `/api/v1/teachers`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/teachers` | Create teacher profile | Required | Admin |
| GET | `/teachers` | List all teachers | Required | All |
| GET | `/teachers/{id}` | Get teacher details | Required | All |
| PUT | `/teachers/{id}` | Update teacher | Required | Admin/Self |
| DELETE | `/teachers/{id}` | Delete teacher | Required | Admin |
| POST | `/teachers/{id}/assign-grade` | Assign grade level | Required | Admin |
| DELETE | `/teachers/{id}/remove-grade/{grade}` | Remove grade | Required | Admin |
| GET | `/teachers/{id}/classes` | Get assigned classes | Required | All |
| GET | `/teachers/{id}/students` | Get all students | Required | Teacher/Admin |
| GET | `/teachers/{id}/schedule` | Get teaching schedule | Required | Teacher/Admin |

### Query Parameters
- `grade_level` - Filter by grade level (1-7)
- `department` - Filter by department
- `status` - Filter by status

---

## Feature 04: Students

### Base Path: `/api/v1/students`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/students` | Create student profile | Required | Admin |
| GET | `/students` | List all students | Required | Teacher/Admin |
| GET | `/students/{id}` | Get student details | Required | Teacher/Admin/Parent/Self |
| PUT | `/students/{id}` | Update student | Required | Admin |
| DELETE | `/students/{id}` | Delete student | Required | Admin |
| POST | `/students/{id}/link-parent` | Link parent to student | Required | Admin |
| DELETE | `/students/{id}/unlink-parent/{parentId}` | Unlink parent | Required | Admin |
| GET | `/students/{id}/parents` | Get student's parents | Required | Teacher/Admin/Self |
| POST | `/students/{id}/promote` | Promote to next grade | Required | Admin |
| GET | `/students/{id}/academic-record` | Get complete record | Required | Teacher/Admin/Parent/Self |
| POST | `/students/{id}/upload-photo` | Upload student photo | Required | Admin |

### Query Parameters
- `grade_level` - Filter by grade (1-7)
- `class_id` - Filter by class
- `status` - Filter by enrollment status
- `parent_id` - Get parent's children

---

## Feature 05: Parents

### Base Path: `/api/v1/parents`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/parents` | Create parent profile | Required | Admin |
| GET | `/parents` | List all parents | Required | Admin |
| GET | `/parents/{id}` | Get parent details | Required | Admin/Self |
| PUT | `/parents/{id}` | Update parent | Required | Admin/Self |
| DELETE | `/parents/{id}` | Delete parent | Required | Admin |
| GET | `/parents/{id}/children` | Get linked students | Required | Admin/Self |
| POST | `/parents/{id}/link-student` | Link student | Required | Admin |
| GET | `/parents/{id}/communications` | Get comm history | Required | Admin/Self |

---

## Feature 06: Subjects

### Base Path: `/api/v1/subjects`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/subjects` | Create subject | Required | Admin |
| GET | `/subjects` | List all subjects | Required | All |
| GET | `/subjects/{id}` | Get subject details | Required | All |
| PUT | `/subjects/{id}` | Update subject | Required | Admin |
| DELETE | `/subjects/{id}` | Delete subject | Required | Admin |
| GET | `/subjects?grade_level={grade}` | Get subjects by grade | Required | All |
| GET | `/subjects/{id}/classes` | Get classes for subject | Required | All |

---

## Feature 07: Rooms

### Base Path: `/api/v1/rooms`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/rooms` | Create room | Required | Admin |
| GET | `/rooms` | List all rooms | Required | All |
| GET | `/rooms/{id}` | Get room details | Required | All |
| PUT | `/rooms/{id}` | Update room | Required | Admin |
| DELETE | `/rooms/{id}` | Delete room | Required | Admin |
| POST | `/rooms/{id}/upload-photo` | Upload room photo | Required | Admin |
| GET | `/rooms?type={type}` | Filter by room type | Required | All |
| GET | `/rooms?available=true` | Get available rooms | Required | All |

---

## Feature 08: Classes

### Base Path: `/api/v1/classes`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/classes` | Create class | Required | Admin |
| GET | `/classes` | List all classes | Required | All |
| GET | `/classes/{id}` | Get class details | Required | All |
| PUT | `/classes/{id}` | Update class | Required | Admin/Teacher |
| DELETE | `/classes/{id}` | Delete class | Required | Admin |
| POST | `/classes/{id}/enroll-student` | Enroll student | Required | Admin/Teacher |
| DELETE | `/classes/{id}/remove-student/{studentId}` | Remove student | Required | Admin/Teacher |
| GET | `/classes/{id}/roster` | Get student roster | Required | Teacher/Admin |
| GET | `/classes/{id}/schedule` | Get class schedule | Required | All |
| PUT | `/classes/{id}/schedule` | Update schedule | Required | Admin/Teacher |

### Query Parameters
- `teacher_id` - Filter by teacher
- `grade_level` - Filter by grade (1-7)
- `quarter` - Filter by quarter (Q1-Q4)
- `subject_id` - Filter by subject
- `academic_year` - Filter by year (2024-2025)

---

## Feature 09: Lessons

### Base Path: `/api/v1/lessons`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/lessons` | Create lesson plan | Required | Teacher/Admin |
| GET | `/lessons` | List all lessons | Required | Teacher/Admin |
| GET | `/lessons/{id}` | Get lesson details | Required | Teacher/Admin |
| PUT | `/lessons/{id}` | Update lesson | Required | Teacher/Admin |
| DELETE | `/lessons/{id}` | Delete lesson | Required | Teacher/Admin |
| POST | `/lessons/{id}/mark-delivered` | Mark as delivered | Required | Teacher |
| POST | `/lessons/{id}/clone` | Clone lesson | Required | Teacher |
| GET | `/lessons/{id}/resources` | Get lesson resources | Required | Teacher/Admin |
| POST | `/lessons/{id}/upload-resource` | Upload resource | Required | Teacher |

### Query Parameters
- `class_id` - Filter by class
- `teacher_id` - Filter by teacher
- `quarter` - Filter by quarter (Q1-Q4)
- `date_range` - Format: start,end (YYYY-MM-DD,YYYY-MM-DD)
- `status` - Filter by status (draft, published, delivered)

---

## Feature 10: Assessments

### Base Path: `/api/v1/assessments`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/assessments` | Create assessment | Required | Teacher/Admin |
| GET | `/assessments` | List all assessments | Required | Teacher/Admin |
| GET | `/assessments/{id}` | Get assessment details | Required | Teacher/Admin/Student |
| PUT | `/assessments/{id}` | Update assessment | Required | Teacher/Admin |
| DELETE | `/assessments/{id}` | Delete assessment | Required | Teacher/Admin |
| POST | `/assessments/{id}/grade-student` | Submit grade | Required | Teacher |
| POST | `/assessments/{id}/bulk-grade` | Grade multiple | Required | Teacher |
| GET | `/assessments/{id}/results` | Get all results | Required | Teacher/Admin |
| GET | `/assessments/{id}/statistics` | Get statistics | Required | Teacher/Admin |
| GET | `/students/{id}/assessments` | Student's assessments | Required | Teacher/Admin/Parent/Self |
| PUT | `/assessments/{id}/results/{studentId}` | Update grade | Required | Teacher |

### Query Parameters
- `class_id` - Filter by class
- `teacher_id` - Filter by teacher
- `quarter` - Filter by quarter (Q1-Q4)
- `assessment_type` - Filter by type (quiz, test, project, oral, homework)
- `status` - Filter by status

---

## Feature 11: Attendance

### Base Path: `/api/v1/attendance`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/attendance` | Mark attendance | Required | Teacher/Admin |
| POST | `/attendance/bulk` | Mark for multiple | Required | Teacher/Admin |
| GET | `/attendance` | List attendance records | Required | Teacher/Admin |
| GET | `/attendance/{id}` | Get record details | Required | Teacher/Admin |
| PUT | `/attendance/{id}` | Update record | Required | Teacher/Admin |
| DELETE | `/attendance/{id}` | Delete record | Required | Admin |
| POST | `/attendance/{id}/notify-parent` | Send notification | Required | Teacher/Admin |
| GET | `/attendance/report` | Generate report | Required | Teacher/Admin |
| GET | `/students/{id}/attendance` | Student attendance | Required | Teacher/Admin/Parent/Self |
| GET | `/attendance/summary` | Attendance summary | Required | Admin |

### Query Parameters
- `student_id` - Filter by student
- `class_id` - Filter by class
- `date_range` - Format: start,end (YYYY-MM-DD,YYYY-MM-DD)
- `status` - Filter by status (present, absent, tardy, excused, sick)
- `month` - Filter by month (1-12)
- `year` - Filter by year (YYYY)

---

## Feature 12: Events

### Base Path: `/api/v1/events`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/events` | Create event | Required | Admin |
| GET | `/events` | List all events | Required | All |
| GET | `/events/{id}` | Get event details | Required | All |
| PUT | `/events/{id}` | Update event | Required | Admin |
| DELETE | `/events/{id}` | Delete event | Required | Admin |
| POST | `/events/{id}/rsvp` | RSVP to event | Required | All |
| DELETE | `/events/{id}/rsvp` | Cancel RSVP | Required | All |
| POST | `/events/{id}/checkin/{userId}` | Check in attendee | Required | Admin/Organizer |
| GET | `/events/{id}/attendees` | Get attendee list | Required | Admin/Organizer |
| GET | `/events/calendar` | Get calendar view | Required | All |

### Query Parameters
- `event_type` - Filter by type
- `date_range` - Format: start,end
- `organizer_id` - Filter by organizer
- `status` - Filter by status (scheduled, in_progress, completed, cancelled)

---

## Feature 13: Activities

### Base Path: `/api/v1/activities`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/activities` | Create activity | Required | Admin |
| GET | `/activities` | List all activities | Required | All |
| GET | `/activities/{id}` | Get activity details | Required | All |
| PUT | `/activities/{id}` | Update activity | Required | Admin |
| DELETE | `/activities/{id}` | Delete activity | Required | Admin |
| POST | `/activities/{id}/enroll` | Enroll student | Required | Admin/Parent |
| DELETE | `/activities/{id}/withdraw/{studentId}` | Withdraw student | Required | Admin/Parent |
| GET | `/activities/{id}/participants` | Get participant list | Required | All |
| GET | `/students/{id}/activities` | Student's activities | Required | Teacher/Admin/Parent/Self |

### Query Parameters
- `activity_type` - Filter by type (sports, club, art, music)
- `grade_level` - Filter by grade
- `coordinator_id` - Filter by coordinator
- `status` - Filter by status

---

## Feature 14: Vendors

### Base Path: `/api/v1/vendors`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/vendors` | Create vendor | Required | Admin |
| GET | `/vendors` | List all vendors | Required | Admin/Vendor |
| GET | `/vendors/{id}` | Get vendor details | Required | Admin/Self |
| PUT | `/vendors/{id}` | Update vendor | Required | Admin/Self |
| DELETE | `/vendors/{id}` | Delete vendor | Required | Admin |
| GET | `/vendors/{id}/events` | Get vendor events | Required | Admin/Self |
| GET | `/vendors/{id}/communications` | Get comm history | Required | Admin/Self |

### Query Parameters
- `vendor_type` - Filter by type (supplies, food, transport, services)
- `status` - Filter by status

---

## Feature 15: Merits

### Base Path: `/api/v1/merits`

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | `/merits` | Award merit points | Required | Teacher/Admin |
| GET | `/merits` | List all merits | Required | Teacher/Admin |
| GET | `/merits/{id}` | Get merit details | Required | Teacher/Admin/Student/Parent |
| PUT | `/merits/{id}` | Update merit | Required | Teacher/Admin |
| DELETE | `/merits/{id}` | Delete merit | Required | Admin |
| GET | `/students/{id}/merits` | Student's merits | Required | Teacher/Admin/Parent/Self |
| GET | `/students/{id}/merit-total` | Total merit points | Required | Teacher/Admin/Parent/Self |
| GET | `/merits/leaderboard` | Merit leaderboard | Required | All |
| GET | `/merits/milestones` | Get milestones | Required | All |
| POST | `/merits/milestones` | Create milestone | Required | Admin |

### Query Parameters
- `student_id` - Filter by student
- `merit_type` - Filter by type (academic, behavior, participation, leadership)
- `quarter` - Filter by quarter (Q1-Q4)
- `class_id` - Filter by class
- `awarded_by` - Filter by teacher

---

## Utility Endpoints

### Health Check
```
GET /api/v1/health
Response: { "status": "healthy", "timestamp": "2025-10-13T10:00:00Z" }
```

### API Documentation
```
GET /docs - Interactive Swagger/OpenAPI documentation
GET /redoc - ReDoc API documentation
```

### System Info
```
GET /api/v1/system/info (Admin only)
Response: { "version": "1.0.0", "environment": "development" }
```

---

## Error Response Format

All errors follow this format:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ],
    "timestamp": "2025-10-13T10:00:00Z",
    "request_id": "uuid"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_ERROR` - Authentication required or failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `DUPLICATE_RESOURCE` - Resource already exists
- `BUSINESS_LOGIC_ERROR` - Business rule violation
- `INTERNAL_ERROR` - Server error

---

## Rate Limiting

All endpoints are rate limited:
- **Authenticated**: 1000 requests per hour per user
- **Unauthenticated**: 100 requests per hour per IP
- **Password Reset**: 5 requests per hour per email

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1697203200
```

---

## Testing the API

### Using curl
```bash
# Get token from Keycloak
TOKEN=$(curl -X POST http://localhost:8080/realms/Green-School-id/protocol/openid-connect/token \
  -d "client_id=Green-School-id" \
  -d "username=admin@greenschool.edu" \
  -d "password=Password123" \
  -d "grant_type=password" | jq -r '.access_token')

# Use token in API call
curl -X GET http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-School-ID: {school_id}"
```

### Using Postman
1. Import OpenAPI spec from http://localhost:8000/docs
2. Set up environment variables:
   - `base_url`: http://localhost:8000/api/v1
   - `token`: {your_keycloak_token}
   - `school_id`: {your_school_id}
3. Add pre-request script to auto-refresh token

---

## Changelog

### Version 1.0 (2025-10-13)
- Initial API documentation
- All 15 features documented
- Complete CRUD operations for all resources
- Multi-tenant support via X-School-ID header
- Keycloak authentication integration

---

## Support

For API issues or questions:
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- See `CLAUDE.md` for development guidance
