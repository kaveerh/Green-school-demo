# Mock Data Audit Report

**Date:** 2025-10-30
**Purpose:** Identify all hardcoded, mock, and placeholder data that needs to be replaced with dynamic values from authentication context

---

## Executive Summary

This audit identified **63+ instances** of mock data across backend and frontend codebases that need to be replaced with dynamic values from authentication/session context.

### Priority Breakdown
- **CRITICAL (26 files)**: Hardcoded school_id `60da2256-81fc-4ca5-bf6b-467b8d371c61`
- **HIGH (28 instances)**: Mock user_id values and TODO comments for auth context
- **MEDIUM (2 files)**: Mock user data in navigation affecting permissions
- **LOW (1 file)**: Mock arrays in forms (subjects, teachers)

---

## CRITICAL: Hardcoded School IDs

### Frontend Files (19 files)

**School ID:** `60da2256-81fc-4ca5-bf6b-467b8d371c61`

| File | Line | Usage |
|------|------|-------|
| `frontend/src/views/LessonForm.vue` | 314 | `const currentSchoolId = ref('60da2256...')` |
| `frontend/src/views/LessonList.vue` | 131 | `const currentSchoolId = ref('60da2256...')` |
| `frontend/src/views/AssessmentForm.vue` | 216 | `const currentSchoolId = ref('60da2256...')` |
| `frontend/src/views/AssessmentList.vue` | 178 | `const currentSchoolId = ref('60da2256...')` |
| `frontend/src/views/AttendanceForm.vue` | 277 | `const schoolId = ref('60da2256...')` |
| `frontend/src/views/AttendanceList.vue` | 248 | `const schoolId = ref('60da2256...')` |
| `frontend/src/views/ActivityForm.vue` | 507 | `const schoolId = '60da2256...'` |
| `frontend/src/views/ActivityList.vue` | 246 | TODO comment |
| `frontend/src/views/EventForm.vue` | 350 | `const schoolId = '60da2256...'` |
| `frontend/src/views/EventList.vue` | 243, 264 | `const schoolId = '60da2256...'` (2x) |
| `frontend/src/views/MeritList.vue` | 190 | Hardcoded school ID for demo |
| `frontend/src/views/VendorList.vue` | 231 | Hardcoded school ID for demo |
| `frontend/src/components/ClassForm.vue` | - | Uses hardcoded school ID |
| `frontend/src/components/ClassList.vue` | 522 | `const schoolId = '60da2256...'` |
| `frontend/src/components/RoomForm.vue` | 328 | Hard-coded school ID comment |
| `frontend/src/components/RoomList.vue` | - | Uses hardcoded school ID |
| `frontend/src/components/SubjectForm.vue` | - | Uses hardcoded school ID |
| `frontend/src/components/SubjectList.vue` | - | Uses hardcoded school ID |
| `frontend/src/stores/dashboardStore.ts` | - | Uses hardcoded school ID |

### Backend Files (7 files)

| File | Line | Context | Count |
|------|------|---------|-------|
| `backend/controllers/parent_controller.py` | 130, 430, 502 | Placeholder for missing auth | 3 |
| `backend/controllers/subject_controller.py` | 128, 196, 367, 402, 442, 486 | Placeholder for missing auth | 6 |
| `backend/utils/auth.py` | 62, 73 | Mock CurrentUser object | 2 |
| `backend/tests/conftest.py` | 85 | Test fixture school ID | 1 |

**Impact:** All multi-tenant queries use this hardcoded value instead of the authenticated user's school context.

**Recommendation:** Create a centralized auth composable/service that retrieves school_id from authentication token/session.

---

## HIGH: Mock User IDs and Auth TODOs

### Backend Controllers - Placeholder User IDs

**Pattern:** `uuid.uuid4()` or hardcoded UUID for `current_user_id`

| Controller | Method | Lines with Mock User IDs | Count |
|------------|--------|--------------------------|-------|
| `assessment_controller.py` | create, update, grade, delete | 54, 136, 297, 363 | 4 |
| `attendance_controller.py` | All methods | 55, 103, 185, 234, 461 | 5 |
| `parent_controller.py` | create, update, delete, link, unlink | 74, 197, 254, 297, 345 | 5 |
| `subject_controller.py` | create, update, delete | 61, 233, 293 | 3 |

**Special Case:** `attendance_controller.py` uses a real user from DB:
```python
current_user_id = uuid.UUID("ea2ad94a-b077-48c2-ae25-6e3e8dc54499")  # Placeholder (real user from DB)
```

### Backend TODO Comments for Auth (28 instances)

All instances follow the pattern: `# TODO: Get current_user_id from auth` or `# TODO: Get current user's school_id from auth if not provided`

| File | TODO Count | Context |
|------|-----------|---------|
| `assessment_controller.py` | 4 | Missing current_user_id |
| `attendance_controller.py` | 5 | Missing current_user_id |
| `parent_controller.py` | 8 | Missing current_user_id and school_id |
| `subject_controller.py` | 11 | Missing current_user_id and school_id |

**Impact:** Audit trail fields (created_by, updated_by) contain random UUIDs instead of actual authenticated users.

**Recommendation:** Implement FastAPI dependency injection for `CurrentUser` similar to how `student_controller.py` uses it:
```python
from utils.auth import CurrentUser, require_admin

async def create_entity(
    current_user: CurrentUser = Depends(require_admin),
    ...
):
    entity = await service.create(created_by_id=current_user.id)
```

---

## HIGH: Mock User IDs in Frontend (12 instances)

### Hardcoded User ID: `bed3ada7-ab32-4a74-84a0-75602181f553`

Used for `created_by_id` parameter in create operations:

| File | Line | Usage |
|------|------|-------|
| `frontend/src/views/ActivityForm.vue` | 508 | `const userId = 'bed3ada7...'` |
| `frontend/src/views/ActivityRoster.vue` | 344, 381, 413, 439 | Used 4 times in roster operations |
| `frontend/src/views/EventForm.vue` | 351 | `const userId = 'bed3ada7...'` |
| `frontend/src/views/EventList.vue` | 303 | `const userId = 'bed3ada7...'` |

### Hardcoded User ID: `ea2ad94a-b077-48c2-ae25-6e3e8dc54499`

Used in attendance controller (see backend section above)

### Hardcoded Teacher ID: `fa4a570e-6ced-42e8-ab2f-beaf59b11a89`

| File | Line | Usage |
|------|------|-------|
| `frontend/src/views/AssessmentList.vue` | 179 | `const currentTeacherId = ref('fa4a570e...')` |

**Impact:** All create operations are attributed to the same hardcoded user instead of the authenticated user.

**Recommendation:** Create an auth store/composable that provides `currentUser.id` from JWT token or session.

---

## MEDIUM: Mock User Data in Navigation

### File: `frontend/src/components/AppNavigation.vue`

**Lines 556-557:**
```typescript
const currentUserName = ref('Admin User')
const currentUserRole = ref('administrator')
```

**Impact:**
- User profile dropdown shows "Admin User" for all users
- All users see administrator-level permissions (lines 571-669)
- Permission checks use mock role instead of actual user role

**Affected Permission Checks (15 computed properties):**
- `canAccessUsers` (line 571)
- `canAccessSchools` (line 578)
- `canAccessTeachers` (line 585)
- `canAccessStudents` (line 592)
- `canAccessParents` (line 599)
- `canAccessSubjects` (line 606)
- `canAccessRooms` (line 613)
- `canAccessClasses` (line 620)
- `canAccessLessons` (line 627)
- `canAccessAssessments` (line 634)
- `canAccessAttendance` (line 641)
- `canAccessEvents` (line 648)
- `canAccessActivities` (line 655)
- `canAccessVendors` (line 662)
- `canAccessMerits` (line 669)

**Recommendation:**
1. Create an auth store with real user data from JWT/session
2. Import and use auth store in AppNavigation
3. Replace hardcoded values with `authStore.currentUser.name` and `authStore.currentUser.role`

---

## MEDIUM: Router Auth Check TODO

### File: `frontend/src/router/index.ts`

**Line 407:**
```typescript
// TODO: Check Keycloak authentication
```

**Impact:** No authentication guard on routes - all routes accessible without login.

**Recommendation:** Implement route guard using Keycloak authentication:
```typescript
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated && to.meta.requiresAuth !== false) {
    await authStore.login()
  } else {
    next()
  }
})
```

---

## LOW: Mock Arrays in Forms

### File: `frontend/src/components/ClassForm.vue`

**Mock subjects array** (referenced but likely in script section):
```typescript
const subjects = ref([
  { id: '94473bd5-c1de-4e8c-9ef3-bde10cacc143', code: 'MATH', name: 'Mathematics' },
  { id: 'subject-2', code: 'ELA', name: 'English Language Arts' },
  // ... more mock subjects
])
```

**Impact:** Class creation form uses hardcoded subjects instead of loading from API.

**Recommendation:** Load subjects from `subjectStore.fetchSubjects()` on component mount.

---

## LOW: Service Layer Auth TODOs

### Token Retrieval Comments

| File | Line | Comment |
|------|------|---------|
| `frontend/src/services/studentService.ts` | 39 | `// TODO: Replace with actual token retrieval from auth store` |
| `frontend/src/services/userService.ts` | 37 | `// TODO: Replace with actual token retrieval from auth store` |
| `frontend/src/services/teacherService.ts` | 37 | `// TODO: Replace with actual token retrieval from auth store` |

**Impact:** Services don't send authentication tokens with API requests.

**Recommendation:**
1. Create auth composable that provides `getAuthToken()` method
2. Update all service methods to include token in headers:
```typescript
const authStore = useAuthStore()
const token = authStore.getToken()
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

---

## Implementation Roadmap

### Phase 1: Backend Authentication (1-2 days)
1. ✅ Verify `utils/auth.py` has working CurrentUser dependency
2. Update all controllers to use `CurrentUser = Depends(require_role)` pattern
3. Remove all `uuid.uuid4()` placeholders
4. Remove all hardcoded school_id placeholders
5. Test audit trail fields contain real user IDs

### Phase 2: Frontend Auth Store (2-3 days)
1. Create `stores/authStore.ts` with Keycloak integration
2. Implement login/logout/token refresh
3. Store user profile (id, name, email, role, school_id) in store
4. Create `useAuth()` composable for easy access

### Phase 3: Replace Mock Data (2-3 days)
1. Replace all `currentSchoolId = ref('60da2256...')` with `authStore.currentUser.school_id`
2. Replace all hardcoded user IDs with `authStore.currentUser.id`
3. Update AppNavigation to use real user data
4. Remove mock arrays, load from API instead

### Phase 4: Router Guards (1 day)
1. Implement route-level authentication guard
2. Add role-based access control
3. Redirect to login if unauthenticated
4. Show 403 page if unauthorized

### Phase 5: Service Layer (1 day)
1. Update all service methods to include auth token
2. Handle 401 responses (token expired)
3. Auto-refresh tokens when needed

### Phase 6: Testing (2 days)
1. Test multi-tenant isolation with different school_ids
2. Test role-based permissions
3. Test audit trail correctness
4. E2E tests with real authentication

**Total Estimated Time:** 9-12 days

---

## Quick Wins (Can be done immediately)

1. **Replace attendance controller user ID** (5 min):
   - `backend/controllers/attendance_controller.py` lines 55, 103, 185, 234, 461
   - Change from hardcoded UUID to `current_user: CurrentUser = Depends(require_admin)`

2. **Fix AppNavigation mock data** (30 min):
   - Create minimal auth store with hardcoded data initially
   - Update AppNavigation to use store instead of local refs
   - Prepare for real auth integration later

3. **Remove ClassForm mock subjects** (15 min):
   - Call `subjectStore.fetchSubjects()` in onMounted
   - Use store data instead of hardcoded array

---

## Files Summary

### Backend Files Needing Changes: 7
- `controllers/assessment_controller.py`
- `controllers/attendance_controller.py`
- `controllers/parent_controller.py`
- `controllers/subject_controller.py`
- `utils/auth.py`
- `tests/conftest.py` (test data only)

### Frontend Files Needing Changes: 26
**Views:**
- `views/LessonForm.vue`
- `views/LessonList.vue`
- `views/AssessmentForm.vue`
- `views/AssessmentList.vue`
- `views/AttendanceForm.vue`
- `views/AttendanceList.vue`
- `views/ActivityForm.vue`
- `views/ActivityList.vue`
- `views/ActivityRoster.vue`
- `views/EventForm.vue`
- `views/EventList.vue`
- `views/MeritList.vue`
- `views/VendorList.vue`

**Components:**
- `components/AppNavigation.vue` ⚠️ **HIGH PRIORITY**
- `components/ClassForm.vue`
- `components/ClassList.vue`
- `components/RoomForm.vue`
- `components/RoomList.vue`
- `components/SubjectForm.vue`
- `components/SubjectList.vue`

**Services:**
- `services/studentService.ts`
- `services/userService.ts`
- `services/teacherService.ts`

**Stores:**
- `stores/dashboardStore.ts`

**Router:**
- `router/index.ts`

---

## Appendix: Search Patterns Used

```bash
# Hardcoded school ID
grep -r "60da2256-81fc-4ca5-bf6b-467b8d371c61"

# Hardcoded user IDs
grep -r "bed3ada7-ab32-4a74-84a0-75602181f553"
grep -r "ea2ad94a-b077-48c2-ae25-6e3e8dc54499"

# TODO comments for auth
grep -rn "TODO.*auth\|TODO.*school_id\|TODO.*user"

# Placeholders
grep -rn "Placeholder\|FIXME\|hardcoded\|mock data"

# UUID generation
grep -rn "uuid\.uuid4()\|uuid\.UUID("

# School ID patterns in frontend
grep -rn "const.*schoolId.*=.*ref("
```

---

**End of Report**
