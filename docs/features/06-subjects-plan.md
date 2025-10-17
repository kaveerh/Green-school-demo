# Feature #6: Subjects Management

**Priority:** 6 of 15
**Status:** Planning
**Dependencies:** Schools (✅), Users (✅)

---

## Overview

The Subjects feature manages the curriculum foundation for the school management system. It defines the academic subjects offered at the school, including core subjects (MATH, ELA, SCIENCE, SOCIAL_STUDIES, ART, PE) and any additional electives or specialized courses.

Subjects are the building blocks for:
- **Classes**: Teachers assigned to teach subjects per grade level
- **Assessments**: Grading and evaluation tied to specific subjects
- **Lessons**: Lesson planning organized by subject
- **Teacher Specializations**: Teachers certified/specialized in subjects

---

## Business Requirements

### Core Subjects (Required)
1. **MATH** - Mathematics
2. **ELA** - English Language Arts (Reading & Writing)
3. **SCIENCE** - General Science
4. **SOCIAL_STUDIES** - Social Studies (History, Geography, Civics)
5. **ART** - Visual Arts
6. **PE** - Physical Education

### Additional Subjects (Optional)
- **MUSIC** - Music Education
- **LIBRARY** - Library/Media Studies
- **TECHNOLOGY** - Computer Science / Technology
- **FOREIGN_LANGUAGE** - Foreign Language (Spanish, French, etc.)
- **DRAMA** - Theater / Performing Arts
- **HEALTH** - Health Education
- **STEM** - Science, Technology, Engineering, Math
- **HOMEROOM** - Homeroom / Advisory
- **OTHER** - Miscellaneous / Custom subjects

### Subject Properties
- **Code**: Unique identifier (e.g., MATH, ELA, SCI)
- **Name**: Display name (e.g., "Mathematics", "English Language Arts")
- **Description**: Detailed subject description
- **Category**: Core, Elective, Enrichment, Remedial
- **Grade Levels**: Which grades (1-7) this subject is taught
- **Color**: UI color code for visual identification
- **Icon**: Optional emoji or icon for UI display
- **Credits**: Optional credit hours (if applicable)
- **Required**: Whether subject is required or elective
- **Active Status**: Enable/disable subjects

---

## Database Schema

### Table: `subjects`

```sql
CREATE TABLE subjects (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,

    -- Subject Information
    code VARCHAR(50) NOT NULL,                    -- e.g., "MATH", "ELA", "SCI"
    name VARCHAR(200) NOT NULL,                   -- e.g., "Mathematics"
    description TEXT,

    -- Categorization
    category VARCHAR(50) DEFAULT 'core',          -- core, elective, enrichment, remedial, other
    subject_type VARCHAR(50),                     -- academic, arts, physical, technical, other

    -- Grade Levels (array of integers 1-7)
    grade_levels INTEGER[] NOT NULL DEFAULT ARRAY[1,2,3,4,5,6,7],

    -- Display Properties
    color VARCHAR(7),                              -- Hex color code (e.g., "#FF5733")
    icon VARCHAR(50),                              -- Emoji or icon identifier
    display_order INTEGER DEFAULT 0,               -- Sort order in UI

    -- Academic Properties
    credits NUMERIC(4,2),                          -- Credit hours (optional)
    is_required BOOLEAN DEFAULT true,              -- Required vs elective

    -- Status
    is_active BOOLEAN DEFAULT true NOT NULL,

    -- Multi-tenant
    -- school_id already defined above

    -- Audit Trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),

    -- Constraints
    CONSTRAINT subjects_code_school_unique UNIQUE(school_id, code),
    CONSTRAINT subjects_category_check CHECK (category IN ('core', 'elective', 'enrichment', 'remedial', 'other')),
    CONSTRAINT subjects_type_check CHECK (subject_type IN ('academic', 'arts', 'physical', 'technical', 'other')),
    CONSTRAINT subjects_grade_levels_check CHECK (grade_levels <@ ARRAY[1,2,3,4,5,6,7]),
    CONSTRAINT subjects_credits_check CHECK (credits IS NULL OR credits >= 0),
    CONSTRAINT subjects_color_format CHECK (color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Indexes
CREATE INDEX idx_subjects_school_id ON subjects(school_id);
CREATE INDEX idx_subjects_code ON subjects(school_id, code);
CREATE INDEX idx_subjects_category ON subjects(category);
CREATE INDEX idx_subjects_active ON subjects(is_active);
CREATE INDEX idx_subjects_deleted ON subjects(deleted_at);
CREATE INDEX idx_subjects_grade_levels ON subjects USING GIN(grade_levels);
```

---

## API Endpoints

### Base URL: `/api/v1/subjects`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/subjects` | Create a new subject |
| GET | `/api/v1/subjects` | List subjects with filters |
| GET | `/api/v1/subjects/{id}` | Get subject by ID |
| PUT | `/api/v1/subjects/{id}` | Update subject |
| DELETE | `/api/v1/subjects/{id}` | Delete subject (soft delete) |
| PATCH | `/api/v1/subjects/{id}/status` | Toggle active status |
| GET | `/api/v1/subjects/code/{code}` | Get subject by code |
| GET | `/api/v1/subjects/category/{category}` | Get subjects by category |
| GET | `/api/v1/subjects/grade/{grade}` | Get subjects for grade level |
| GET | `/api/v1/subjects/statistics/summary` | Get subject statistics |

---

## API Request/Response Examples

### 1. Create Subject

**Request:**
```http
POST /api/v1/subjects
Content-Type: application/json

{
  "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
  "code": "MATH",
  "name": "Mathematics",
  "description": "Core mathematics curriculum covering arithmetic, geometry, and algebra for grades 1-7",
  "category": "core",
  "subject_type": "academic",
  "grade_levels": [1, 2, 3, 4, 5, 6, 7],
  "color": "#2196F3",
  "icon": "🔢",
  "is_required": true,
  "is_active": true
}
```

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "school_id": "60da2256-81fc-4ca5-bf6b-467b8d371c61",
  "code": "MATH",
  "name": "Mathematics",
  "description": "Core mathematics curriculum...",
  "category": "core",
  "subject_type": "academic",
  "grade_levels": [1, 2, 3, 4, 5, 6, 7],
  "color": "#2196F3",
  "icon": "🔢",
  "display_order": 0,
  "credits": null,
  "is_required": true,
  "is_active": true,
  "created_at": "2025-10-17T10:30:00Z",
  "updated_at": "2025-10-17T10:30:00Z"
}
```

### 2. List Subjects

**Request:**
```http
GET /api/v1/subjects?school_id=60da2256-81fc-4ca5-bf6b-467b8d371c61&category=core&is_active=true&page=1&limit=20
```

**Response:**
```json
{
  "subjects": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "code": "MATH",
      "name": "Mathematics",
      "category": "core",
      "color": "#2196F3",
      "icon": "🔢",
      "is_required": true,
      "is_active": true
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "code": "ELA",
      "name": "English Language Arts",
      "category": "core",
      "color": "#4CAF50",
      "icon": "📚",
      "is_required": true,
      "is_active": true
    }
  ],
  "total": 6,
  "page": 1,
  "limit": 20
}
```

### 3. Get Statistics

**Request:**
```http
GET /api/v1/subjects/statistics/summary?school_id=60da2256-81fc-4ca5-bf6b-467b8d371c61
```

**Response:**
```json
{
  "total_subjects": 10,
  "active_subjects": 8,
  "inactive_subjects": 2,
  "by_category": {
    "core": 6,
    "elective": 3,
    "enrichment": 1
  },
  "by_type": {
    "academic": 5,
    "arts": 2,
    "physical": 2,
    "technical": 1
  },
  "required_subjects": 6,
  "elective_subjects": 4
}
```

---

## Validation Rules

### Create/Update Subject
- ✅ `school_id`: Required, must exist
- ✅ `code`: Required, 2-50 characters, alphanumeric + underscore, unique per school
- ✅ `name`: Required, 1-200 characters
- ✅ `description`: Optional, max 2000 characters
- ✅ `category`: Must be one of: core, elective, enrichment, remedial, other
- ✅ `subject_type`: Must be one of: academic, arts, physical, technical, other
- ✅ `grade_levels`: Array of integers 1-7, at least one grade required
- ✅ `color`: Optional, valid hex color format (#RRGGBB)
- ✅ `icon`: Optional, max 50 characters
- ✅ `credits`: Optional, numeric >= 0
- ✅ `is_required`: Boolean, default true
- ✅ `is_active`: Boolean, default true

### Business Rules
- Subject code must be unique within a school
- Cannot delete subject if it has associated classes
- Grade levels must be valid (1-7 only)
- Color must be valid hex format if provided
- Core subjects should be required by default
- At least one grade level must be selected

---

## Sample Data

```json
[
  {
    "code": "MATH",
    "name": "Mathematics",
    "description": "Core mathematics curriculum covering arithmetic, algebra, and geometry",
    "category": "core",
    "subject_type": "academic",
    "grade_levels": [1, 2, 3, 4, 5, 6, 7],
    "color": "#2196F3",
    "icon": "🔢",
    "is_required": true
  },
  {
    "code": "ELA",
    "name": "English Language Arts",
    "description": "Reading, writing, grammar, and literature",
    "category": "core",
    "subject_type": "academic",
    "grade_levels": [1, 2, 3, 4, 5, 6, 7],
    "color": "#4CAF50",
    "icon": "📚",
    "is_required": true
  },
  {
    "code": "SCIENCE",
    "name": "Science",
    "description": "General science including life, earth, and physical sciences",
    "category": "core",
    "subject_type": "academic",
    "grade_levels": [1, 2, 3, 4, 5, 6, 7],
    "color": "#9C27B0",
    "icon": "🔬",
    "is_required": true
  },
  {
    "code": "SOCIAL_STUDIES",
    "name": "Social Studies",
    "description": "History, geography, civics, and social sciences",
    "category": "core",
    "subject_type": "academic",
    "grade_levels": [1, 2, 3, 4, 5, 6, 7],
    "color": "#FF9800",
    "icon": "🌍",
    "is_required": true
  },
  {
    "code": "ART",
    "name": "Art",
    "description": "Visual arts including drawing, painting, and sculpture",
    "category": "core",
    "subject_type": "arts",
    "grade_levels": [1, 2, 3, 4, 5, 6, 7],
    "color": "#E91E63",
    "icon": "🎨",
    "is_required": true
  },
  {
    "code": "PE",
    "name": "Physical Education",
    "description": "Physical fitness, sports, and health",
    "category": "core",
    "subject_type": "physical",
    "grade_levels": [1, 2, 3, 4, 5, 6, 7],
    "color": "#F44336",
    "icon": "⚽",
    "is_required": true
  }
]
```

---

## Frontend Components

### SubjectList.vue
**Purpose:** Display list of subjects with search and filtering

**Features:**
- Table view with columns: Icon, Code, Name, Category, Type, Grade Levels, Status, Actions
- Search by code or name
- Filter by category (core, elective, etc.)
- Filter by subject type (academic, arts, physical, technical)
- Filter by active status
- Sort by display order, name, or category
- Pagination
- Color-coded badges for categories
- Edit, Delete, Toggle Status actions
- Create new subject button

**Layout:**
```
┌─────────────────────────────────────────────┐
│ 📊 Subjects                  [+ New Subject]│
├─────────────────────────────────────────────┤
│ Search: [____________] 🔍                   │
│ Category: [All ▼] Type: [All ▼] Status: ☑️ Active │
├─────────────────────────────────────────────┤
│ Statistics:                                 │
│ Total: 10 | Core: 6 | Elective: 3 | Other: 1│
├─────────────────────────────────────────────┤
│ Icon Code  Name              Category Grade │
│ 🔢   MATH  Mathematics       Core     1-7  │
│ 📚   ELA   English Lang...   Core     1-7  │
│ 🔬   SCI   Science          Core     1-7  │
│ 🌍   SS    Social Studies   Core     1-7  │
│ 🎨   ART   Art              Core     1-7  │
│ ⚽   PE    Physical Ed       Core     1-7  │
├─────────────────────────────────────────────┤
│ ← Previous | Page 1 of 1 | Next →         │
└─────────────────────────────────────────────┘
```

### SubjectForm.vue
**Purpose:** Create/Edit subject

**Sections:**
1. **Basic Information**
   - Code (required, uppercase, unique)
   - Name (required)
   - Description (textarea)

2. **Classification**
   - Category (dropdown: core, elective, enrichment, remedial, other)
   - Subject Type (dropdown: academic, arts, physical, technical, other)
   - Is Required (checkbox)
   - Is Active (checkbox)

3. **Grade Levels**
   - Checkboxes for grades 1-7 (at least one required)

4. **Display Properties**
   - Color picker (hex color)
   - Icon selector (emoji picker or text input)
   - Display Order (number input)

5. **Academic Properties**
   - Credits (optional, numeric)

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Create Subject                    [Cancel] [Save]│
├─────────────────────────────────────────────┤
│ Basic Information                           │
│ Code*: [MATH__________]                    │
│ Name*: [Mathematics___________]            │
│ Description:                                │
│ [________________________________]          │
│                                             │
├─────────────────────────────────────────────┤
│ Classification                              │
│ Category*: [Core ▼]                        │
│ Type*: [Academic ▼]                        │
│ ☑️ Required  ☑️ Active                      │
├─────────────────────────────────────────────┤
│ Grade Levels* (Select at least one)        │
│ ☑️ 1  ☑️ 2  ☑️ 3  ☑️ 4  ☑️ 5  ☑️ 6  ☑️ 7   │
├─────────────────────────────────────────────┤
│ Display Properties                          │
│ Color: [🎨 #2196F3] Icon: [🔢]            │
│ Display Order: [0]                         │
├─────────────────────────────────────────────┤
│ Academic Properties                         │
│ Credits: [___] (optional)                  │
└─────────────────────────────────────────────┘
```

---

## TypeScript Types

```typescript
// Subject Category
export type SubjectCategory = 'core' | 'elective' | 'enrichment' | 'remedial' | 'other'

// Subject Type
export type SubjectType = 'academic' | 'arts' | 'physical' | 'technical' | 'other'

// Subject Interface
export interface Subject {
  id: string
  school_id: string
  code: string
  name: string
  description?: string
  category: SubjectCategory
  subject_type?: SubjectType
  grade_levels: number[]
  color?: string
  icon?: string
  display_order: number
  credits?: number
  is_required: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string
}

// Subject Create Input
export interface SubjectCreateInput {
  school_id: string
  code: string
  name: string
  description?: string
  category: SubjectCategory
  subject_type?: SubjectType
  grade_levels: number[]
  color?: string
  icon?: string
  display_order?: number
  credits?: number
  is_required?: boolean
  is_active?: boolean
}

// Subject Update Input
export interface SubjectUpdateInput {
  name?: string
  description?: string
  category?: SubjectCategory
  subject_type?: SubjectType
  grade_levels?: number[]
  color?: string
  icon?: string
  display_order?: number
  credits?: number
  is_required?: boolean
  is_active?: boolean
}

// Subject List Response
export interface SubjectListResponse {
  subjects: Subject[]
  total: number
  page: number
  limit: number
}

// Subject Statistics
export interface SubjectStatistics {
  total_subjects: number
  active_subjects: number
  inactive_subjects: number
  by_category: Record<string, number>
  by_type: Record<string, number>
  required_subjects: number
  elective_subjects: number
}

// Helper functions
export function getSubjectCategoryLabel(category: SubjectCategory): string
export function getSubjectTypeLabel(type: SubjectType): string
export function formatGradeLevels(grades: number[]): string
```

---

## Implementation Checklist

### Database Layer
- [ ] Create subject ORM model
- [ ] Add school relationship
- [ ] Create indexes for performance
- [ ] Add constraints and validations
- [ ] Write sample data script

### Backend API Layer
- [ ] Create SubjectRepository with methods:
  - [ ] `create()`, `get_by_id()`, `get_by_code()`
  - [ ] `get_by_school()`, `get_by_category()`, `get_by_grade()`
  - [ ] `update()`, `delete()`, `toggle_status()`
  - [ ] `search()`, `get_statistics()`
- [ ] Create SubjectService with business logic
- [ ] Create validation schemas (Pydantic)
- [ ] Create SubjectController with 10 endpoints
- [ ] Register routes in main.py
- [ ] Test all endpoints manually

### Frontend Foundation
- [ ] Create TypeScript types
- [ ] Create SubjectService API client
- [ ] Create SubjectStore (Pinia)

### Frontend Components
- [ ] Create SubjectList.vue
- [ ] Create SubjectForm.vue
- [ ] Add color picker component
- [ ] Add icon selector component

### Routing & Navigation
- [ ] Add subject routes to Vue Router
- [ ] Update AppNavigation menu

### Testing
- [ ] Write backend unit tests
- [ ] Write API integration tests
- [ ] Write E2E tests (Playwright)

### Documentation
- [ ] Update API documentation
- [ ] Create user guide
- [ ] Update CHANGELOG

---

## Success Criteria

### Backend
- [ ] All 10 API endpoints functional
- [ ] Multi-tenant isolation enforced
- [ ] Validation working correctly
- [ ] Statistics endpoint accurate
- [ ] Soft delete implemented
- [ ] Audit logging complete

### Frontend
- [ ] List view shows all subjects
- [ ] Search and filters work
- [ ] Create/edit forms validate correctly
- [ ] Color picker functional
- [ ] Grade level selection works
- [ ] Statistics display correctly
- [ ] Delete confirmation works
- [ ] Navigation integrated

### Data Integrity
- [ ] Subject codes unique per school
- [ ] Grade levels validated (1-7)
- [ ] Color format validated
- [ ] Cannot delete subjects with classes
- [ ] At least one grade level required

---

## Future Enhancements

1. **Subject Prerequisites**: Define prerequisite relationships
2. **Subject Standards**: Link to educational standards (Common Core, etc.)
3. **Subject Resources**: Attach textbooks, materials, links
4. **Subject Outcomes**: Define learning outcomes/objectives
5. **Subject Budgets**: Track subject-specific budgets
6. **Subject Scheduling**: Define periods/schedule constraints
7. **Subject Capacity**: Max students per subject
8. **Cross-Grade Subjects**: Support for multi-grade subjects
9. **Subject Teams**: Multiple teachers per subject
10. **Custom Fields**: School-specific subject attributes

---

## Notes

- Subjects are foundational for Classes, Assessments, and Lessons
- Core subjects (MATH, ELA, SCIENCE, SOCIAL_STUDIES, ART, PE) should be created by default
- Subject codes should follow consistent naming (uppercase, no spaces)
- Colors help with visual identification in schedules and reports
- Grade levels determine which classes can be created for a subject
- Soft delete prevents data loss and maintains referential integrity

---

**Created:** October 17, 2025
**Last Updated:** October 17, 2025
**Status:** Ready for Implementation
