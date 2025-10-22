# Feature #9: Lessons - Implementation Plan

## Overview
Lessons feature enables teachers to plan, create, and manage lesson plans tied to their classes. Supports curriculum alignment, resource attachments, learning objectives, and lesson status tracking.

## Database Schema

### Table: `lessons`

```sql
CREATE TABLE lessons (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES teachers(id) ON DELETE RESTRICT,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE RESTRICT,

    -- Identification
    title VARCHAR(200) NOT NULL,
    lesson_number INTEGER NOT NULL,  -- Sequential within class

    -- Scheduling
    scheduled_date DATE NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 45,  -- Lesson duration

    -- Content
    description TEXT,
    learning_objectives TEXT[],  -- Array of learning objectives
    materials_needed TEXT[],  -- Array of materials/resources
    curriculum_standards TEXT[],  -- Array of standards (e.g., "CCSS.MATH.3.OA.A.1")

    -- Lesson Plan
    introduction TEXT,  -- Lesson opening
    main_activity TEXT,  -- Core lesson content
    assessment TEXT,  -- How to assess learning
    homework TEXT,  -- Homework assignment
    notes TEXT,  -- Teacher notes

    -- Resources
    attachments JSONB DEFAULT '[]',  -- Array of file attachments
    links TEXT[],  -- External resource links

    -- Status & Progress
    status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft, scheduled, in_progress, completed, cancelled
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    actual_duration_minutes INTEGER,  -- Actual time spent

    -- Reflection
    reflection TEXT,  -- Post-lesson reflection
    what_went_well TEXT,
    what_to_improve TEXT,
    modifications_needed TEXT,

    -- Display
    color VARCHAR(7),  -- Hex color for calendar view
    is_template BOOLEAN DEFAULT FALSE,  -- Can be used as template
    template_id UUID REFERENCES lessons(id) ON DELETE SET NULL,  -- Created from template

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES users(id),

    -- Constraints
    CONSTRAINT lessons_status_check CHECK (status IN ('draft', 'scheduled', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT lessons_lesson_number_positive CHECK (lesson_number > 0),
    CONSTRAINT lessons_duration_positive CHECK (duration_minutes > 0),
    CONSTRAINT lessons_unique_number UNIQUE (class_id, lesson_number, deleted_at)
);

-- Indexes
CREATE INDEX idx_lessons_school_id ON lessons(school_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_lessons_class_id ON lessons(class_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_lessons_teacher_id ON lessons(teacher_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_lessons_subject_id ON lessons(subject_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_lessons_scheduled_date ON lessons(scheduled_date) WHERE deleted_at IS NULL;
CREATE INDEX idx_lessons_status ON lessons(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_lessons_deleted_at ON lessons(deleted_at);
```

## Business Rules

### Lesson Numbering
- Lesson numbers are sequential within each class
- Lesson numbers start at 1 for each class
- Deleted lessons don't break the sequence
- Lesson numbers must be unique within a class

### Status Workflow
- **draft**: Lesson is being planned
- **scheduled**: Lesson is ready and scheduled
- **in_progress**: Lesson is currently being taught
- **completed**: Lesson has been taught and completed
- **cancelled**: Lesson was cancelled

### Validation Rules
- Title: Required, 1-200 characters
- Lesson number: Required, positive integer
- Scheduled date: Required, cannot be more than 1 year in past or 2 years in future
- Duration: Required, 1-240 minutes (4 hours max)
- Status: Required, must be valid status value
- Teacher must belong to same school as class
- Subject must match class subject
- Completion percentage: 0-100

### Template System
- Teachers can mark lessons as templates
- Templates can be reused for future lessons
- Creating from template copies all content but resets status to draft
- Template ID tracks the source template

## API Endpoints

### Lesson CRUD

#### 1. Create Lesson
```http
POST /api/v1/lessons?school_id={school_id}
Content-Type: application/json

{
  "class_id": "uuid",
  "teacher_id": "uuid",
  "subject_id": "uuid",
  "title": "Introduction to Multiplication",
  "lesson_number": 5,
  "scheduled_date": "2024-11-15",
  "duration_minutes": 45,
  "description": "Students will learn basic multiplication concepts",
  "learning_objectives": [
    "Understand multiplication as repeated addition",
    "Solve simple multiplication problems"
  ],
  "materials_needed": [
    "Whiteboard",
    "Multiplication flash cards",
    "Student workbooks"
  ],
  "curriculum_standards": ["CCSS.MATH.3.OA.A.1"],
  "introduction": "Start with a warm-up activity...",
  "main_activity": "Teach multiplication concept...",
  "assessment": "Exit ticket with 5 problems",
  "homework": "Workbook pages 15-16",
  "notes": "Remember to review previous lesson",
  "attachments": [],
  "links": ["https://example.com/multiplication-games"],
  "color": "#4CAF50",
  "is_template": false
}

Response: 201 Created
{
  "id": "uuid",
  "school_id": "uuid",
  "class_id": "uuid",
  "teacher_id": "uuid",
  "subject_id": "uuid",
  "title": "Introduction to Multiplication",
  "lesson_number": 5,
  "scheduled_date": "2024-11-15",
  "duration_minutes": 45,
  "status": "draft",
  "completion_percentage": 0,
  ...
  "created_at": "2024-10-22T10:00:00Z",
  "updated_at": "2024-10-22T10:00:00Z"
}
```

#### 2. List Lessons (with filters)
```http
GET /api/v1/lessons?school_id={school_id}&page=1&limit=50&class_id={class_id}&teacher_id={teacher_id}&subject_id={subject_id}&status=scheduled&start_date=2024-11-01&end_date=2024-11-30

Response: 200 OK
{
  "lessons": [...],
  "total": 45,
  "page": 1,
  "limit": 50,
  "total_pages": 1
}
```

#### 3. Get Lesson by ID
```http
GET /api/v1/lessons/{id}

Response: 200 OK
{
  "id": "uuid",
  "title": "Introduction to Multiplication",
  ...
}
```

#### 4. Update Lesson
```http
PUT /api/v1/lessons/{id}
Content-Type: application/json

{
  "title": "Updated title",
  "status": "completed",
  "completion_percentage": 100,
  "actual_duration_minutes": 50,
  "reflection": "Lesson went well, students engaged"
}

Response: 200 OK
```

#### 5. Delete Lesson
```http
DELETE /api/v1/lessons/{id}

Response: 204 No Content
```

### Status Management

#### 6. Update Lesson Status
```http
PATCH /api/v1/lessons/{id}/status
Content-Type: application/json

{
  "status": "completed",
  "completion_percentage": 100,
  "actual_duration_minutes": 50
}

Response: 200 OK
```

#### 7. Start Lesson (Set to In Progress)
```http
PATCH /api/v1/lessons/{id}/start

Response: 200 OK
```

#### 8. Complete Lesson
```http
PATCH /api/v1/lessons/{id}/complete
Content-Type: application/json

{
  "completion_percentage": 100,
  "actual_duration_minutes": 50,
  "reflection": "Lesson reflection...",
  "what_went_well": "Students were engaged",
  "what_to_improve": "Need more examples",
  "modifications_needed": "Add visual aids"
}

Response: 200 OK
```

### Query Endpoints

#### 9. Get Lessons by Class
```http
GET /api/v1/lessons/class/{class_id}?status=scheduled&start_date=2024-11-01&end_date=2024-11-30

Response: 200 OK
[...]
```

#### 10. Get Lessons by Teacher
```http
GET /api/v1/lessons/teacher/{teacher_id}?school_id={school_id}&start_date=2024-11-01&end_date=2024-11-30

Response: 200 OK
[...]
```

#### 11. Get Lessons by Date Range
```http
GET /api/v1/lessons/calendar?school_id={school_id}&start_date=2024-11-01&end_date=2024-11-30&teacher_id={teacher_id}

Response: 200 OK
[...]
```

#### 12. Search Lessons
```http
GET /api/v1/lessons/search?school_id={school_id}&query=multiplication&page=1&limit=50

Response: 200 OK
{
  "lessons": [...],
  "total": 5,
  "page": 1,
  "limit": 50,
  "total_pages": 1
}
```

### Template Management

#### 13. Create from Template
```http
POST /api/v1/lessons/from-template/{template_id}
Content-Type: application/json

{
  "class_id": "uuid",
  "scheduled_date": "2024-12-01"
}

Response: 201 Created
```

#### 14. Get Templates
```http
GET /api/v1/lessons/templates?school_id={school_id}&subject_id={subject_id}&teacher_id={teacher_id}

Response: 200 OK
[...]
```

#### 15. Mark as Template
```http
PATCH /api/v1/lessons/{id}/template
Content-Type: application/json

{
  "is_template": true
}

Response: 200 OK
```

### Statistics

#### 16. Get Lesson Statistics
```http
GET /api/v1/lessons/statistics?school_id={school_id}&teacher_id={teacher_id}&start_date=2024-11-01&end_date=2024-11-30

Response: 200 OK
{
  "total_lessons": 45,
  "by_status": {
    "draft": 5,
    "scheduled": 20,
    "in_progress": 2,
    "completed": 15,
    "cancelled": 3
  },
  "by_subject": {
    "MATH": 15,
    "ELA": 12,
    "SCI": 10,
    "SS": 8
  },
  "average_duration": 47.5,
  "completion_rate": 85.5,
  "total_teaching_minutes": 2137
}
```

## Frontend Components

### LessonList Component
**Features:**
- Calendar view and list view toggle
- Filters: class, teacher, subject, status, date range
- Search by title or content
- Statistics dashboard
- Quick status updates
- Template indicators
- Color-coded by subject/status

### LessonForm Component
**Sections:**
1. **Basic Information**
   - Title, lesson number, class
   - Scheduled date, duration
   - Status

2. **Planning**
   - Description
   - Learning objectives (dynamic list)
   - Materials needed (dynamic list)
   - Curriculum standards (dynamic list)

3. **Lesson Plan**
   - Introduction
   - Main activity
   - Assessment
   - Homework

4. **Resources**
   - File attachments
   - Links (dynamic list)

5. **Reflection** (After completion)
   - Completion percentage
   - Actual duration
   - Reflection notes
   - What went well
   - What to improve
   - Modifications needed

6. **Display Settings**
   - Color
   - Template checkbox

### LessonCalendar Component
**Features:**
- Month/week/day views
- Drag and drop to reschedule
- Color-coded lessons
- Quick view popup
- Filter by class/subject/teacher
- Today highlight

## TypeScript Types

```typescript
export type LessonStatus = 'draft' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled';

export interface Attachment {
  id: string;
  name: string;
  url: string;
  size: number;
  type: string;
  uploaded_at: string;
}

export interface Lesson {
  id: string;
  school_id: string;
  class_id: string;
  teacher_id: string;
  subject_id: string;
  title: string;
  lesson_number: number;
  scheduled_date: string;
  duration_minutes: number;
  description: string | null;
  learning_objectives: string[];
  materials_needed: string[];
  curriculum_standards: string[];
  introduction: string | null;
  main_activity: string | null;
  assessment: string | null;
  homework: string | null;
  notes: string | null;
  attachments: Attachment[];
  links: string[];
  status: LessonStatus;
  completion_percentage: number;
  actual_duration_minutes: number | null;
  reflection: string | null;
  what_went_well: string | null;
  what_to_improve: string | null;
  modifications_needed: string | null;
  color: string | null;
  is_template: boolean;
  template_id: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;

  // Computed fields
  class_name?: string;
  subject_name?: string;
  teacher_name?: string;
}

export interface LessonCreateInput {
  class_id: string;
  teacher_id: string;
  subject_id: string;
  title: string;
  lesson_number: number;
  scheduled_date: string;
  duration_minutes?: number;
  description?: string | null;
  learning_objectives?: string[];
  materials_needed?: string[];
  curriculum_standards?: string[];
  introduction?: string | null;
  main_activity?: string | null;
  assessment?: string | null;
  homework?: string | null;
  notes?: string | null;
  attachments?: Attachment[];
  links?: string[];
  color?: string | null;
  is_template?: boolean;
}

export interface LessonUpdateInput {
  title?: string;
  lesson_number?: number;
  scheduled_date?: string;
  duration_minutes?: number;
  description?: string | null;
  learning_objectives?: string[];
  materials_needed?: string[];
  curriculum_standards?: string[];
  introduction?: string | null;
  main_activity?: string | null;
  assessment?: string | null;
  homework?: string | null;
  notes?: string | null;
  attachments?: Attachment[];
  links?: string[];
  status?: LessonStatus;
  completion_percentage?: number;
  actual_duration_minutes?: number | null;
  reflection?: string | null;
  what_went_well?: string | null;
  what_to_improve?: string | null;
  modifications_needed?: string | null;
  color?: string | null;
  is_template?: boolean;
}

export interface LessonStatistics {
  total_lessons: number;
  by_status: Record<LessonStatus, number>;
  by_subject: Record<string, number>;
  average_duration: number;
  completion_rate: number;
  total_teaching_minutes: number;
}
```

## Sample Data

```javascript
const sampleLessons = [
  {
    title: "Introduction to Multiplication",
    lesson_number: 5,
    scheduled_date: "2024-11-15",
    duration_minutes: 45,
    description: "Students will learn basic multiplication concepts using visual aids and manipulatives",
    learning_objectives: [
      "Understand multiplication as repeated addition",
      "Solve simple multiplication problems (2x2 through 5x5)",
      "Identify real-world applications of multiplication"
    ],
    materials_needed: [
      "Whiteboard and markers",
      "Multiplication flash cards",
      "Student workbooks",
      "Counters or manipulatives",
      "Projector"
    ],
    curriculum_standards: [
      "CCSS.MATH.3.OA.A.1",
      "CCSS.MATH.3.OA.A.3"
    ],
    introduction: "Begin with a quick review of addition. Ask students: 'If we have 3 groups of 4 apples, how many apples do we have total?' Use this to transition into multiplication.",
    main_activity: "1. Explain multiplication as repeated addition\n2. Demonstrate with visual aids\n3. Practice with manipulatives\n4. Independent work time",
    assessment: "Exit ticket: Students solve 5 multiplication problems (2x3, 3x4, 4x2, 5x3, 2x5)",
    homework: "Complete workbook pages 15-16, practice multiplication facts 2-5",
    notes: "Remember to emphasize the commutative property. Some students may need extra support with visualization.",
    links: [
      "https://example.com/multiplication-games",
      "https://example.com/parent-resources"
    ],
    status: "scheduled",
    color: "#4CAF50"
  },
  {
    title: "Plant Life Cycle",
    lesson_number: 8,
    scheduled_date: "2024-11-16",
    duration_minutes: 60,
    description: "Explore the stages of plant growth from seed to flowering plant",
    learning_objectives: [
      "Identify the stages of the plant life cycle",
      "Understand what plants need to grow",
      "Observe and record plant growth over time"
    ],
    materials_needed: [
      "Seeds (beans work well)",
      "Soil",
      "Small pots",
      "Water",
      "Plant life cycle poster"
    ],
    curriculum_standards: [
      "NGSS.2-LS2-1",
      "NGSS.3-LS1-1"
    ],
    introduction: "Show time-lapse video of plant growing. Discuss what students noticed.",
    main_activity: "Students will plant seeds and create observation journals. Teach the stages: seed, germination, seedling, adult plant, flowering, and seed production.",
    assessment: "Students draw and label the plant life cycle",
    homework: "Observe and draw your plant for the next 2 weeks",
    status: "scheduled",
    color: "#8BC34A"
  },
  {
    title: "Persuasive Writing Introduction",
    lesson_number: 12,
    scheduled_date: "2024-11-14",
    duration_minutes: 45,
    description: "Introduction to persuasive writing techniques and structure",
    learning_objectives: [
      "Understand the purpose of persuasive writing",
      "Identify persuasive techniques in sample texts",
      "Begin drafting a persuasive paragraph"
    ],
    materials_needed: [
      "Sample persuasive texts",
      "Writing notebooks",
      "Anchor chart materials"
    ],
    curriculum_standards: [
      "CCSS.ELA-LITERACY.W.4.1"
    ],
    introduction: "Read aloud a persuasive letter. Ask: What is the author trying to convince us to do?",
    main_activity: "Create anchor chart of persuasive techniques. Students analyze sample texts and identify techniques used.",
    assessment: "Students write topic sentence for their own persuasive paragraph",
    homework: "Find one example of persuasive writing at home (advertisement, sign, etc.)",
    status: "completed",
    completion_percentage: 100,
    actual_duration_minutes: 48,
    reflection: "Lesson went well. Students were engaged with the real-world examples.",
    what_went_well: "The advertisement analysis activity was very successful",
    what_to_improve: "Need more time for independent writing",
    modifications_needed: "Split into two lessons - techniques vs. writing practice",
    color: "#2196F3"
  }
];
```

## Implementation Checklist

### Backend
- [ ] Create Lesson ORM model
- [ ] Create LessonRepository with 16+ methods
- [ ] Create LessonService with business logic
- [ ] Create Pydantic schemas
- [ ] Create LessonController with 16 endpoints
- [ ] Register routes in main.py
- [ ] Test all endpoints
- [ ] Commit backend implementation

### Frontend
- [ ] Create TypeScript types
- [ ] Create LessonService API client
- [ ] Create LessonStore Pinia store
- [ ] Create LessonList component
- [ ] Create LessonForm component
- [ ] Create LessonCalendar component (optional)
- [ ] Add routing
- [ ] Add navigation
- [ ] Test and commit frontend

### Testing
- [ ] Backend unit tests
- [ ] API integration tests
- [ ] Frontend E2E tests
- [ ] CRUD operations verification
- [ ] Template system testing
- [ ] Status workflow testing

## Notes
- Lessons are class-specific and teacher-owned
- Support for rich text editing in lesson plan sections
- File attachment system (future: integrate with cloud storage)
- Template system allows reusability across classes/years
- Reflection section appears only after lesson completion
- Calendar integration for visual planning
- Statistics help teachers track teaching time and completion rates
