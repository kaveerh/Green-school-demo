# Feature #5: Parents Management

**Priority:** 5 of 15
**Status:** 🚧 In Progress
**Dependencies:** Users (✅), Schools (✅), Students (✅)

---

## Overview

Parents module manages parent/guardian accounts and their relationships with students. Supports multiple parents per student and multiple students per parent (family relationships).

---

## Database Schema

### Table: `parents`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `school_id` | UUID | FOREIGN KEY, NOT NULL | School association |
| `user_id` | UUID | FOREIGN KEY, NOT NULL, UNIQUE | User account (must have 'parent' persona) |
| `occupation` | VARCHAR(100) | | Parent's occupation |
| `workplace` | VARCHAR(200) | | Workplace name/address |
| `phone_mobile` | VARCHAR(20) | | Mobile phone number |
| `phone_work` | VARCHAR(20) | | Work phone number |
| `preferred_contact_method` | VARCHAR(20) | | Email, phone, sms |
| `emergency_contact` | BOOLEAN | DEFAULT FALSE | Can be contacted in emergencies |
| `pickup_authorized` | BOOLEAN | DEFAULT FALSE | Authorized to pick up students |
| `receives_newsletter` | BOOLEAN | DEFAULT TRUE | Opt-in for newsletters |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL | Last update time |
| `created_by_id` | UUID | FOREIGN KEY | Who created the record |
| `updated_by_id` | UUID | FOREIGN KEY | Who last updated |
| `deleted_at` | TIMESTAMP | | Soft delete timestamp |
| `deleted_by_id` | UUID | FOREIGN KEY | Who deleted the record |

### Table: `parent_student_relationships` (Already exists in student.py)

Links parents to students with relationship type.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `school_id` | UUID | FOREIGN KEY, NOT NULL | School association |
| `parent_id` | UUID | FOREIGN KEY, NOT NULL | Parent reference |
| `student_id` | UUID | FOREIGN KEY, NOT NULL | Student reference |
| `relationship_type` | VARCHAR(50) | NOT NULL | mother, father, guardian, etc. |
| `is_primary_contact` | BOOLEAN | DEFAULT FALSE | Primary contact for student |
| `has_legal_custody` | BOOLEAN | DEFAULT TRUE | Legal custody rights |
| `has_pickup_permission` | BOOLEAN | DEFAULT TRUE | Can pick up student |
| `created_at` | TIMESTAMP | NOT NULL | Relationship creation time |
| `updated_at` | TIMESTAMP | NOT NULL | Last update time |

---

## API Endpoints

### Parents CRUD

1. **POST `/api/v1/parents`** - Create parent
   - Body: `ParentCreateSchema`
   - Returns: `ParentResponseSchema`
   - Auth: Administrator only

2. **GET `/api/v1/parents`** - List parents (paginated, filtered)
   - Query params: `page`, `limit`, `search`, `school_id`
   - Returns: `{ parents: [], total, page, limit }`
   - Auth: Administrator, Teacher

3. **GET `/api/v1/parents/{id}`** - Get parent by ID
   - Returns: `ParentResponseSchema` with relationships
   - Auth: Administrator, Teacher, Parent (own only)

4. **PUT `/api/v1/parents/{id}`** - Update parent
   - Body: `ParentUpdateSchema`
   - Returns: `ParentResponseSchema`
   - Auth: Administrator

5. **DELETE `/api/v1/parents/{id}`** - Soft delete parent
   - Returns: Success message
   - Auth: Administrator only

### Relationship Management

6. **POST `/api/v1/parents/{parent_id}/link-student`** - Link parent to student
   - Body: `{ student_id, relationship_type, is_primary_contact, has_legal_custody, has_pickup_permission }`
   - Returns: Relationship object
   - Auth: Administrator

7. **DELETE `/api/v1/parents/{parent_id}/unlink-student/{student_id}`** - Remove relationship
   - Returns: Success message
   - Auth: Administrator

8. **GET `/api/v1/parents/{parent_id}/students`** - Get parent's children
   - Returns: List of students with relationship details
   - Auth: Administrator, Teacher, Parent (own only)

### Search and Filters

9. **GET `/api/v1/parents/search`** - Search parents
   - Query: `q` (name, email, phone)
   - Returns: Matching parents
   - Auth: Administrator, Teacher

10. **GET `/api/v1/parents/by-student/{student_id}`** - Get student's parents
    - Returns: List of parents for a student
    - Auth: Administrator, Teacher

### Statistics

11. **GET `/api/v1/parents/statistics`** - Get parent statistics
    - Returns: Total parents, emergency contacts, newsletter subscribers
    - Auth: Administrator

---

## Business Logic

### Parent Creation
- Must link to existing user with 'parent' persona
- One user can be parent at only one school (multi-school parents need multiple accounts)
- Validate phone numbers format
- Default preferences (newsletter: true, emergency_contact: false)

### Student Linking
- Parent can have multiple children (students)
- Student can have multiple parents/guardians
- Only one primary contact per student recommended (not enforced)
- Relationship types: mother, father, guardian, stepmother, stepfather, grandparent, foster_parent, other
- Track legal custody and pickup permissions separately

### Contact Preferences
- Preferred contact method: email, phone, sms, app_notification
- Newsletter opt-in/opt-out
- Emergency contact designation
- Pickup authorization separate from legal custody

### Privacy & GDPR
- Audit all CRUD operations
- Parental consent required for student data access
- Right to deletion (soft delete with audit trail)
- Data export capability

---

## Frontend Components

### ParentList.vue
- Searchable table of parents
- Columns: Name, Email, Phone, Children, Contact Prefs, Actions
- Filters: School, Has Children, Emergency Contact, Newsletter
- Actions: View, Edit, Delete, Link Student

### ParentForm.vue
- Create/Edit parent
- Sections:
  - Basic Information (user selection, phone numbers)
  - Employment (occupation, workplace)
  - Contact Preferences (method, emergency, pickup, newsletter)
  - Student Relationships (link/unlink children)
- Validation: Required fields, phone format
- UserSelector component for user_id

### ParentDetail.vue
- View parent details
- List of children with relationship types
- Contact history (future)
- Communication log (future)

### ParentStudentLinkDialog.vue
- Modal for linking parent to student
- Select student (UserSelector or StudentSelector)
- Choose relationship type
- Set primary contact flag
- Set legal custody and pickup permissions

---

## Pinia Store (parentStore.ts)

### State
```typescript
{
  parents: Parent[]
  selectedParent: Parent | null
  statistics: ParentStatistics | null
  isLoading: boolean
  error: string | null
  pagination: { page, limit, total }
}
```

### Actions
- `fetchParents(filters)`
- `fetchParentById(id)`
- `createParent(data)`
- `updateParent(id, data)`
- `deleteParent(id)`
- `linkStudent(parentId, linkData)`
- `unlinkStudent(parentId, studentId)`
- `fetchParentStudents(parentId)`
- `fetchStudentParents(studentId)`
- `fetchStatistics()`
- `searchParents(query)`

---

## TypeScript Types

```typescript
export type ContactMethod = 'email' | 'phone' | 'sms' | 'app_notification'

export type RelationshipType =
  | 'mother'
  | 'father'
  | 'guardian'
  | 'stepmother'
  | 'stepfather'
  | 'grandparent'
  | 'foster_parent'
  | 'other'

export interface Parent {
  id: string
  school_id: string
  user_id: string
  occupation?: string
  workplace?: string
  phone_mobile?: string
  phone_work?: string
  preferred_contact_method?: ContactMethod
  emergency_contact: boolean
  pickup_authorized: boolean
  receives_newsletter: boolean
  created_at: string
  updated_at: string

  // Relations (populated)
  user?: User
  students?: Student[]
  relationships?: ParentStudentRelationship[]
}

export interface ParentStudentRelationship {
  id: string
  school_id: string
  parent_id: string
  student_id: string
  relationship_type: RelationshipType
  is_primary_contact: boolean
  has_legal_custody: boolean
  has_pickup_permission: boolean
  created_at: string
  updated_at: string

  // Relations
  parent?: Parent
  student?: Student
}

export interface ParentCreateInput {
  school_id: string
  user_id: string
  occupation?: string
  workplace?: string
  phone_mobile?: string
  phone_work?: string
  preferred_contact_method?: ContactMethod
  emergency_contact?: boolean
  pickup_authorized?: boolean
  receives_newsletter?: boolean
}

export interface ParentUpdateInput {
  occupation?: string
  workplace?: string
  phone_mobile?: string
  phone_work?: string
  preferred_contact_method?: ContactMethod
  emergency_contact?: boolean
  pickup_authorized?: boolean
  receives_newsletter?: boolean
}

export interface ParentStudentLinkInput {
  student_id: string
  relationship_type: RelationshipType
  is_primary_contact?: boolean
  has_legal_custody?: boolean
  has_pickup_permission?: boolean
}

export interface ParentStatistics {
  total_parents: number
  emergency_contacts: number
  pickup_authorized: number
  newsletter_subscribers: number
  parents_with_children: number
  parents_without_children: number
}
```

---

## Validation Rules

### Parent Creation
- `user_id`: Required, must exist, must have 'parent' persona
- `school_id`: Required, must exist
- `phone_mobile`: Optional, must match phone format if provided
- `phone_work`: Optional, must match phone format if provided
- `preferred_contact_method`: Must be one of: email, phone, sms, app_notification

### Parent Update
- All fields optional
- Phone format validation if provided
- Cannot change `user_id` or `school_id`

### Student Linking
- `student_id`: Required, must exist, must belong to same school
- `relationship_type`: Required, must be valid type
- `is_primary_contact`: Boolean, default false
- `has_legal_custody`: Boolean, default true
- `has_pickup_permission`: Boolean, default true

---

## Security & Permissions

### Administrator
- Full CRUD on all parents
- Link/unlink students
- View all relationships
- Access statistics

### Teacher
- View parents (read-only)
- View parent-student relationships
- Search parents
- Cannot modify

### Parent
- View own profile only
- View own children
- Cannot view other parents
- Cannot modify relationships

### Student
- View own parents
- Read-only access

---

## Sample Data (5 Parents)

```python
parents = [
  {
    "user_id": "parent-user-uuid-1",  # John Smith
    "school_id": SCHOOL_ID,
    "occupation": "Software Engineer",
    "workplace": "Tech Corp",
    "phone_mobile": "+1-555-0101",
    "phone_work": "+1-555-0102",
    "preferred_contact_method": "email",
    "emergency_contact": True,
    "pickup_authorized": True,
    "receives_newsletter": True
  },
  {
    "user_id": "parent-user-uuid-2",  # Sarah Smith
    "school_id": SCHOOL_ID,
    "occupation": "Teacher",
    "workplace": "Lincoln Elementary",
    "phone_mobile": "+1-555-0103",
    "preferred_contact_method": "phone",
    "emergency_contact": True,
    "pickup_authorized": True,
    "receives_newsletter": True
  },
  {
    "user_id": "parent-user-uuid-3",  # Maria Garcia
    "school_id": SCHOOL_ID,
    "occupation": "Nurse",
    "workplace": "City Hospital",
    "phone_mobile": "+1-555-0104",
    "phone_work": "+1-555-0105",
    "preferred_contact_method": "sms",
    "emergency_contact": True,
    "pickup_authorized": True,
    "receives_newsletter": False
  },
  {
    "user_id": "parent-user-uuid-4",  # David Johnson
    "school_id": SCHOOL_ID,
    "occupation": "Attorney",
    "workplace": "Johnson & Associates",
    "phone_mobile": "+1-555-0106",
    "phone_work": "+1-555-0107",
    "preferred_contact_method": "email",
    "emergency_contact": False,
    "pickup_authorized": True,
    "receives_newsletter": True
  },
  {
    "user_id": "parent-user-uuid-5",  # Lisa Chen
    "school_id": SCHOOL_ID,
    "occupation": "Business Owner",
    "workplace": "Chen Family Restaurant",
    "phone_mobile": "+1-555-0108",
    "preferred_contact_method": "phone",
    "emergency_contact": True,
    "pickup_authorized": True,
    "receives_newsletter": True
  }
]

# Sample relationships
relationships = [
  {
    "parent_id": "john-smith-parent-id",
    "student_id": "emma-smith-student-id",
    "relationship_type": "father",
    "is_primary_contact": True,
    "has_legal_custody": True,
    "has_pickup_permission": True
  },
  {
    "parent_id": "sarah-smith-parent-id",
    "student_id": "emma-smith-student-id",
    "relationship_type": "mother",
    "is_primary_contact": False,
    "has_legal_custody": True,
    "has_pickup_permission": True
  }
]
```

---

## Testing Checklist

### Backend API Tests
- [ ] Create parent with valid data
- [ ] Create parent with invalid user_id
- [ ] List parents with pagination
- [ ] Filter parents by search query
- [ ] Get parent by ID
- [ ] Update parent information
- [ ] Delete parent (soft delete)
- [ ] Link parent to student
- [ ] Unlink parent from student
- [ ] Get parent's children
- [ ] Get student's parents
- [ ] Get statistics

### Frontend E2E Tests
- [ ] Navigate to parents list
- [ ] Search for parent by name
- [ ] Create new parent
- [ ] Edit parent details
- [ ] Link parent to student
- [ ] Unlink parent from student
- [ ] View parent's children
- [ ] Delete parent

---

## Implementation Order

1. **Database** (Parent model)
2. **Repository** (ParentRepository with specialized queries)
3. **Service** (ParentService with business logic)
4. **Controller** (ParentController with 11 endpoints)
5. **Schemas** (Pydantic validation schemas)
6. **Routes** (Register in main.py)
7. **Frontend Types** (TypeScript interfaces)
8. **Service** (ParentService API client)
9. **Store** (Pinia parentStore)
10. **Components** (List, Form, Detail views)
11. **Routing** (Vue Router configuration)
12. **Navigation** (Add to menu)
13. **Tests** (E2E tests with Playwright)

---

## Success Criteria

✅ Parent CRUD operations work end-to-end
✅ Parent-student linking functional
✅ Multiple parents per student supported
✅ Multiple children per parent supported
✅ Contact preferences tracked
✅ Emergency contact and pickup authorization managed
✅ Multi-tenant isolation enforced
✅ Audit logging complete
✅ All tests passing

---

**Status:** Ready to implement
**Estimated Time:** 4-6 hours
**Next Feature:** #6 Subjects
