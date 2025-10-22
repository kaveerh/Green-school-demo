# Feature #8: Classes (Class Management)

**Priority**: 8 of 15
**Dependencies**: Users (#1), Schools (#2), Teachers (#3), Students (#4), Subjects (#6), Rooms (#7)
**Status**: In Progress
**Last Updated**: 2025-10-22

## Overview

Class management for creating and managing class sections that combine teachers, subjects, students, and rooms. Supports quarter-based organization, enrollment management, scheduling, and capacity tracking.

## Business Requirements

### Class Management
- Administrators can create, update, and delete classes
- Each class belongs to a school (multi-tenant)
- Class codes must be unique within a school
- Classes are associated with a single subject, teacher, and grade level
- Classes are organized by academic quarters (Q1, Q2, Q3, Q4)
- Support room assignment for physical location
- Track maximum student capacity and current enrollment
- Schedule information (days, times)

### Student Enrollment
- Students can be enrolled in multiple classes
- Track enrollment status (enrolled, dropped, completed, withdrawn)
- Enrollment date tracking
- Final grade recording
- Maximum capacity enforcement

### Scheduling
- Days of week (Monday-Friday)
- Start and end times
- Room assignment with conflict detection

## Database Schema

### Table: classes

```sql
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,

    -- Identification
    code VARCHAR(50) NOT NULL,  -- Unique per school
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Associations
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,
    teacher_id UUID NOT NULL REFERENCES teachers(id) ON DELETE RESTRICT,
    room_id UUID REFERENCES rooms(id) ON DELETE SET NULL,

    -- Classification
    grade_level INTEGER NOT NULL,  -- 1-7
    quarter VARCHAR(10) NOT NULL,  -- Q1, Q2, Q3, Q4
    academic_year VARCHAR(20) NOT NULL,  -- e.g., "2024-2025"

    -- Capacity
    max_students INTEGER NOT NULL DEFAULT 30,
    current_enrollment INTEGER DEFAULT 0,

    -- Schedule (JSONB for flexibility)
    schedule JSONB,  -- {days: ["Monday", "Wednesday"], start_time: "09:00", end_time: "10:30"}

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Display
    color VARCHAR(7),  -- #RRGGBB
    display_order INTEGER DEFAULT 0,

    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),

    -- Constraints
    CONSTRAINT uq_classes_code_school UNIQUE(school_id, code),
    CONSTRAINT chk_classes_grade CHECK (grade_level BETWEEN 1 AND 7),
    CONSTRAINT chk_classes_quarter CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    CONSTRAINT chk_classes_max_students CHECK (max_students > 0),
    CONSTRAINT chk_classes_enrollment CHECK (current_enrollment >= 0 AND current_enrollment <= max_students)
);

-- Indexes
CREATE INDEX idx_classes_school_id ON classes(school_id);
CREATE INDEX idx_classes_subject_id ON classes(subject_id);
CREATE INDEX idx_classes_teacher_id ON classes(teacher_id);
CREATE INDEX idx_classes_room_id ON classes(room_id);
CREATE INDEX idx_classes_grade_level ON classes(grade_level);
CREATE INDEX idx_classes_quarter ON classes(quarter);
CREATE INDEX idx_classes_academic_year ON classes(academic_year);
CREATE INDEX idx_classes_active ON classes(is_active);
CREATE INDEX idx_classes_deleted_at ON classes(deleted_at);
```

### Table: student_classes (Junction Table)

```sql
CREATE TABLE student_classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,

    -- Enrollment
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    drop_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'enrolled',  -- enrolled, dropped, completed, withdrawn

    -- Grades
    final_grade VARCHAR(5),  -- A+, A, B+, etc.
    final_score DECIMAL(5, 2),  -- 0-100

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uq_student_class UNIQUE(student_id, class_id),
    CONSTRAINT chk_student_classes_status CHECK (status IN ('enrolled', 'dropped', 'completed', 'withdrawn')),
    CONSTRAINT chk_student_classes_score CHECK (final_score IS NULL OR (final_score >= 0 AND final_score <= 100))
);

-- Indexes
CREATE INDEX idx_student_classes_student_id ON student_classes(student_id);
CREATE INDEX idx_student_classes_class_id ON student_classes(class_id);
CREATE INDEX idx_student_classes_status ON student_classes(status);
```

## API Endpoints

### 1. Create Class
**POST** `/api/v1/classes`

**Request Body**:
```json
{
  "school_id": "uuid",
  "code": "MATH-5-Q1-A",
  "name": "5th Grade Math - Section A",
  "description": "Advanced mathematics for 5th graders",
  "subject_id": "uuid",
  "teacher_id": "uuid",
  "room_id": "uuid",
  "grade_level": 5,
  "quarter": "Q1",
  "academic_year": "2024-2025",
  "max_students": 30,
  "schedule": {
    "days": ["Monday", "Wednesday", "Friday"],
    "start_time": "09:00",
    "end_time": "10:30"
  },
  "is_active": true,
  "color": "#2196F3"
}
```

**Response**: Class object with relationships populated

**Validation**:
- `school_id` (required, valid UUID)
- `code` (required, 1-50 chars, unique per school)
- `name` (required, 1-200 chars)
- `subject_id` (required, must exist and belong to school)
- `teacher_id` (required, must exist and belong to school)
- `room_id` (optional, must exist and belong to school)
- `grade_level` (required, 1-7)
- `quarter` (required, Q1/Q2/Q3/Q4)
- `academic_year` (required, format YYYY-YYYY)
- `max_students` (required, positive integer)

### 2. List Classes
**GET** `/api/v1/classes`

**Query Parameters**:
- `school_id` (required)
- `subject_id` - Filter by subject
- `teacher_id` - Filter by teacher
- `room_id` - Filter by room
- `grade_level` - Filter by grade
- `quarter` - Filter by quarter
- `academic_year` - Filter by year
- `is_active` - Filter by status
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 50)

**Response**:
```json
{
  "classes": [Class],
  "total": 45,
  "page": 1,
  "limit": 50
}
```

### 3. Get Class by ID
**GET** `/api/v1/classes/{id}`

**Response**: Class object with:
- Subject details
- Teacher details
- Room details
- Current enrollment count
- Student list

### 4. Get Class by Code
**GET** `/api/v1/classes/code/{code}`

**Query Parameters**:
- `school_id` (required)

**Response**: Single Class object

### 5. Update Class
**PUT** `/api/v1/classes/{id}`

**Request Body**: Partial Class object (all fields optional except code cannot change)

**Response**: Updated Class object

**Validation**: Same as create, but code cannot be modified

### 6. Delete Class
**DELETE** `/api/v1/classes/{id}`

**Response**: Success message

**Soft Delete**: Sets `deleted_at` timestamp

**Note**: Cannot delete class with enrolled students (must drop all students first)

### 7. Toggle Class Status
**PATCH** `/api/v1/classes/{id}/status`

**Request Body**:
```json
{
  "is_active": true
}
```

**Response**: Updated Class object

### 8. Get Classes by Teacher
**GET** `/api/v1/classes/teacher/{teacher_id}`

**Query Parameters**:
- `school_id` (required)
- `quarter` (optional)
- `academic_year` (optional)

**Response**: Array of Class objects

### 9. Get Classes by Subject
**GET** `/api/v1/classes/subject/{subject_id}`

**Query Parameters**:
- `school_id` (required)
- `grade_level` (optional)
- `quarter` (optional)

**Response**: Array of Class objects

### 10. Get Classes by Room
**GET** `/api/v1/classes/room/{room_id}`

**Query Parameters**:
- `school_id` (required)

**Response**: Array of Class objects

### 11. Search Classes
**GET** `/api/v1/classes/search/query`

**Query Parameters**:
- `q` (required) - Search query
- `school_id` (required)
- `page` - Page number
- `limit` - Results per page

**Response**: Paginated list of matching classes

### 12. Get Class Statistics
**GET** `/api/v1/classes/statistics/summary`

**Query Parameters**:
- `school_id` (optional)

**Response**:
```json
{
  "total_classes": 45,
  "active_classes": 42,
  "inactive_classes": 3,
  "by_grade": {
    "1": 6,
    "2": 6,
    "3": 7,
    "4": 7,
    "5": 6,
    "6": 6,
    "7": 7
  },
  "by_quarter": {
    "Q1": 12,
    "Q2": 11,
    "Q3": 11,
    "Q4": 11
  },
  "by_subject": {
    "MATH": 8,
    "ELA": 8,
    "SCIENCE": 7
  },
  "total_enrollment": 856,
  "average_class_size": 19.9,
  "capacity_utilization": 66.3
}
```

### Student Enrollment Endpoints

### 13. Enroll Student
**POST** `/api/v1/classes/{class_id}/students/{student_id}`

**Request Body**:
```json
{
  "enrollment_date": "2024-09-01"
}
```

**Response**: StudentClass enrollment record

**Validation**:
- Class must not be full
- Student must be in correct grade level
- Student cannot be enrolled twice

### 14. Get Class Students
**GET** `/api/v1/classes/{class_id}/students`

**Response**: Array of Student objects with enrollment details

### 15. Drop Student
**DELETE** `/api/v1/classes/{class_id}/students/{student_id}`

**Response**: Success message

**Note**: Sets drop_date and status to 'dropped'

### 16. Update Student Grade
**PATCH** `/api/v1/classes/{class_id}/students/{student_id}/grade`

**Request Body**:
```json
{
  "final_grade": "A",
  "final_score": 93.5
}
```

**Response**: Updated StudentClass record

## Sample Data (5 Classes)

```sql
-- Sample classes for testing
INSERT INTO classes (school_id, code, name, subject_id, teacher_id, room_id, grade_level, quarter, academic_year, max_students, schedule) VALUES

-- 5th Grade Math
('{school_id}', 'MATH-5-Q1-A', '5th Grade Math - Section A', '{math_subject_id}', '{teacher1_id}', '{room101_id}', 5, 'Q1', '2024-2025', 30,
 '{"days": ["Monday", "Wednesday", "Friday"], "start_time": "09:00", "end_time": "10:30"}'::jsonb),

-- 3rd Grade ELA
('{school_id}', 'ELA-3-Q1-B', '3rd Grade English - Section B', '{ela_subject_id}', '{teacher2_id}', '{room102_id}', 3, 'Q1', '2024-2025', 25,
 '{"days": ["Tuesday", "Thursday"], "start_time": "10:00", "end_time": "11:30"}'::jsonb),

-- 6th Grade Science
('{school_id}', 'SCI-6-Q2-A', '6th Grade Science - Lab', '{science_subject_id}', '{teacher3_id}', '{lab_room_id}', 6, 'Q2', '2024-2025', 24,
 '{"days": ["Monday", "Wednesday"], "start_time": "13:00", "end_time": "14:30"}'::jsonb),

-- 1st Grade Art
('{school_id}', 'ART-1-Q1-A', '1st Grade Art', '{art_subject_id}', '{teacher4_id}', '{art_room_id}', 1, 'Q1', '2024-2025', 20,
 '{"days": ["Friday"], "start_time": "14:00", "end_time": "15:00"}'::jsonb),

-- 7th Grade PE
('{school_id}', 'PE-7-Q3-A', '7th Grade Physical Education', '{pe_subject_id}', '{teacher5_id}', '{gym_id}', 7, 'Q3', '2024-2025', 35,
 '{"days": ["Monday", "Wednesday", "Friday"], "start_time": "11:00", "end_time": "12:00"}'::jsonb);
```

## Validation Rules

### Class Code
- Required for creation
- 1-50 characters
- Unique per school
- Recommended format: {SUBJECT}-{GRADE}-{QUARTER}-{SECTION}
- Cannot be changed after creation (immutable)

### Grade Level
- Required
- Must be 1-7
- Should match assigned teacher's grade levels
- Student enrollments must match class grade

### Quarter
- Required
- Must be Q1, Q2, Q3, or Q4
- Used for filtering and reporting

### Academic Year
- Required
- Format: YYYY-YYYY (e.g., "2024-2025")
- Used for historical tracking

### Max Students
- Required
- Positive integer
- Current enrollment cannot exceed max
- Warning if enrollment > 90% capacity

### Schedule
- Optional JSONB object
- If provided, must have days array and times
- Days: Monday-Friday
- Times: HH:MM format (24-hour)
- start_time must be before end_time

### Teacher Assignment
- Required
- Teacher must belong to school
- Teacher should have grade_level in their grades array
- One teacher per class (no team teaching in v1)

### Subject Assignment
- Required
- Subject must belong to school
- Subject should include grade_level in grade_levels array

### Room Assignment
- Optional
- Room must belong to school
- Check for scheduling conflicts (same room, overlapping times)

## Frontend Components

### ClassList.vue
**Purpose**: Display and manage class inventory

**Features**:
- Table view with code, name, subject, teacher, room, grade, quarter, enrollment
- Search by code, name
- Filter by subject, teacher, grade, quarter, academic year, status
- Sort by code, grade, enrollment, quarter
- Statistics summary cards
- Quick actions: view roster, edit, toggle status, delete
- Enrollment progress bars
- Capacity warnings
- Pagination

**Columns**:
1. Code
2. Name
3. Subject (badge with color)
4. Teacher name
5. Room
6. Grade
7. Quarter (badge)
8. Enrollment (X/Y with progress bar)
9. Status (active/inactive)
10. Actions

### ClassForm.vue
**Purpose**: Create and edit classes

**Sections**:

1. **Basic Information**
   - Code (immutable in edit mode)
   - Name
   - Description

2. **Associations**
   - Subject (dropdown, filtered by school)
   - Teacher (dropdown, filtered by school and grade)
   - Room (dropdown, filtered by school, optional)

3. **Classification**
   - Grade Level (1-7 dropdown)
   - Quarter (Q1-Q4 dropdown)
   - Academic Year (text input or dropdown)

4. **Capacity**
   - Max Students (number input)
   - Current Enrollment (readonly in edit mode)

5. **Schedule**
   - Days of Week (checkboxes)
   - Start Time (time picker)
   - End Time (time picker)

6. **Status**
   - Active (checkbox)

7. **Preview**
   - Visual preview of class card

**Validation**:
- Client-side validation for required fields
- Code format validation
- Grade level validation (1-7)
- Quarter validation
- Academic year format
- Max students positive integer
- Start time before end time
- Real-time duplicate code checking

### ClassDetail.vue
**Purpose**: View class details and manage students

**Sections**:
1. Class information display
2. Teacher and subject details
3. Room and schedule
4. Student roster with:
   - Add student button
   - Student list with enrollment date
   - Drop student action
   - Grade entry fields
5. Enrollment statistics

## TypeScript Types

### frontend/src/types/class.ts

```typescript
/**
 * Class Types
 */

// Quarter Type
export type Quarter = 'Q1' | 'Q2' | 'Q3' | 'Q4'

// Enrollment Status
export type EnrollmentStatus = 'enrolled' | 'dropped' | 'completed' | 'withdrawn'

// Day of Week
export type DayOfWeek = 'Monday' | 'Tuesday' | 'Wednesday' | 'Thursday' | 'Friday'

// Schedule Interface
export interface ClassSchedule {
  days: DayOfWeek[]
  start_time: string  // HH:MM format
  end_time: string    // HH:MM format
}

// Class Interface
export interface Class {
  id: string
  school_id: string

  // Identification
  code: string
  name: string
  description?: string

  // Associations
  subject_id: string
  teacher_id: string
  room_id?: string

  // Populated relationships
  subject_name?: string
  subject_code?: string
  teacher_name?: string
  room_number?: string

  // Classification
  grade_level: number
  quarter: Quarter
  academic_year: string

  // Capacity
  max_students: number
  current_enrollment: number

  // Schedule
  schedule?: ClassSchedule

  // Status
  is_active: boolean

  // Display
  color?: string
  display_order: number

  // Audit
  created_at: string
  updated_at: string
  deleted_at?: string

  // Computed
  is_full?: boolean
  capacity_percent?: number
  available_seats?: number
}

// Student Class (Enrollment)
export interface StudentClass {
  id: string
  student_id: string
  class_id: string
  enrollment_date: string
  drop_date?: string
  status: EnrollmentStatus
  final_grade?: string
  final_score?: number
  created_at: string
  updated_at: string

  // Populated
  student_name?: string
}

// Class Create Input
export interface ClassCreateInput {
  school_id: string
  code: string
  name: string
  description?: string
  subject_id: string
  teacher_id: string
  room_id?: string
  grade_level: number
  quarter: Quarter
  academic_year: string
  max_students: number
  schedule?: ClassSchedule
  is_active?: boolean
  color?: string
  display_order?: number
}

// Class Update Input
export interface ClassUpdateInput {
  name?: string
  description?: string
  subject_id?: string
  teacher_id?: string
  room_id?: string
  grade_level?: number
  quarter?: Quarter
  academic_year?: string
  max_students?: number
  schedule?: ClassSchedule
  is_active?: boolean
  color?: string
  display_order?: number
}

// Class Search Parameters
export interface ClassSearchParams {
  school_id?: string
  subject_id?: string
  teacher_id?: string
  room_id?: string
  grade_level?: number
  quarter?: Quarter
  academic_year?: string
  is_active?: boolean
  page?: number
  limit?: number
}

// Class List Response
export interface ClassListResponse {
  classes: Class[]
  total: number
  page: number
  limit: number
}

// Class Statistics
export interface ClassStatistics {
  total_classes: number
  active_classes: number
  inactive_classes: number
  by_grade: Record<string, number>
  by_quarter: Record<string, number>
  by_subject: Record<string, number>
  total_enrollment: number
  average_class_size: number
  capacity_utilization: number
}

/**
 * Helper Functions
 */

export function getQuarterLabel(quarter: Quarter): string {
  const labels: Record<Quarter, string> = {
    Q1: 'Quarter 1',
    Q2: 'Quarter 2',
    Q3: 'Quarter 3',
    Q4: 'Quarter 4'
  }
  return labels[quarter]
}

export function getAllQuarters(): Quarter[] {
  return ['Q1', 'Q2', 'Q3', 'Q4']
}

export function formatSchedule(schedule: ClassSchedule): string {
  if (!schedule || !schedule.days || schedule.days.length === 0) {
    return 'No schedule'
  }

  const daysStr = schedule.days.join(', ')
  const timeStr = `${schedule.start_time} - ${schedule.end_time}`
  return `${daysStr} • ${timeStr}`
}

export function calculateCapacityPercent(current: number, max: number): number {
  if (max === 0) return 0
  return Math.round((current / max) * 100)
}

export function isClassFull(current: number, max: number): boolean {
  return current >= max
}

export function getAvailableSeats(current: number, max: number): number {
  return Math.max(0, max - current)
}

export function getCapacityColor(percent: number): string {
  if (percent >= 100) return '#e74c3c'  // Red - Full
  if (percent >= 90) return '#f39c12'   // Orange - Nearly full
  if (percent >= 75) return '#f1c40f'   // Yellow - High
  return '#42b883'                       // Green - Good
}

export function isValidAcademicYear(year: string): boolean {
  return /^\d{4}-\d{4}$/.test(year)
}

export function formatAcademicYear(year: string): string {
  return year.trim()
}

export function getDaysOfWeek(): DayOfWeek[] {
  return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
}

export function isValidTime(time: string): boolean {
  return /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/.test(time)
}

export function formatClassCode(code: string): string {
  return code.toUpperCase().trim()
}

export function getEnrollmentStatusLabel(status: EnrollmentStatus): string {
  const labels: Record<EnrollmentStatus, string> = {
    enrolled: 'Enrolled',
    dropped: 'Dropped',
    completed: 'Completed',
    withdrawn: 'Withdrawn'
  }
  return labels[status]
}

export function getEnrollmentStatusColor(status: EnrollmentStatus): string {
  const colors: Record<EnrollmentStatus, string> = {
    enrolled: '#42b883',
    dropped: '#f39c12',
    completed: '#3498db',
    withdrawn: '#e74c3c'
  }
  return colors[status]
}
```

## Implementation Checklist

### Database Phase
- [x] Design schema
- [ ] Create migration SQL
- [ ] Apply migration
- [ ] Create ORM models (Class, StudentClass)
- [ ] Add sample data (5 classes)
- [ ] Test constraints and indexes

### API Phase
- [ ] Create ClassRepository
- [ ] Create StudentClassRepository
- [ ] Create ClassService
- [ ] Create ClassController
- [ ] Create Pydantic schemas
- [ ] Register routes in main.py
- [ ] Test all 16 endpoints manually
- [ ] Document API

### Frontend Phase
- [ ] Create TypeScript types
- [ ] Create ClassService
- [ ] Create ClassStore
- [ ] Create ClassList.vue
- [ ] Create ClassForm.vue
- [ ] Create ClassDetail.vue (student roster)
- [ ] Add routes to Vue Router
- [ ] Update AppNavigation.vue
- [ ] Test CRUD operations

### Testing Phase
- [ ] Backend unit tests
- [ ] API integration tests
- [ ] Playwright E2E tests
- [ ] Multi-tenancy verification

### Documentation Phase
- [ ] Update feature plan with completion status
- [ ] Update API documentation
- [ ] Commit to git

## Success Criteria

- [ ] All 16 API endpoints working
- [ ] Class CRUD operations complete
- [ ] Student enrollment/drop working
- [ ] Multi-tenant isolation verified
- [ ] Search and filtering functional
- [ ] Statistics dashboard accurate
- [ ] Capacity enforcement working
- [ ] Schedule validation working
- [ ] Frontend components responsive
- [ ] All tests passing

## Notes

- Classes are the core entity that ties together teachers, subjects, students, and rooms
- Quarter-based organization is critical for academic calendar
- Enrollment capacity must be enforced
- Schedule conflicts should be detected (future enhancement)
- Student grade levels must match class grade level
- Room conflicts should be checked (future enhancement)
- Current enrollment updated automatically on student add/drop

---

**Status**: Database schema designed, ready for implementation
**Next Step**: Create ORM models and migration
