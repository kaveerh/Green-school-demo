# Feature #13: Activities - Implementation Plan

## Overview
Activities feature enables management of extracurricular activities (sports, clubs, arts, music) with student enrollment tracking, scheduling, and coordinator assignment. Supports grade-level restrictions, capacity limits, and cost tracking.

## Database Schema

### Table: `activities`

```sql
CREATE TABLE activities (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    coordinator_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Identification
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50), -- Unique activity code (e.g., "FB-2024", "CHESS-CLUB")

    -- Classification
    activity_type VARCHAR(50) NOT NULL, -- sports, club, art, music, academic, other
    category VARCHAR(100), -- More specific: basketball, chess, painting, etc.

    -- Description
    description TEXT,

    -- Eligibility
    grade_levels INT[] NOT NULL, -- Array of eligible grades (1-7)
    max_participants INT, -- Maximum enrollment capacity
    min_participants INT, -- Minimum required to run activity

    -- Scheduling
    schedule JSONB DEFAULT '{}', -- {"days": ["Monday", "Wednesday"], "start_time": "15:30", "end_time": "17:00"}
    start_date DATE, -- When activity season begins
    end_date DATE, -- When activity season ends

    -- Location & Logistics
    location VARCHAR(255), -- Where activity takes place
    room_id UUID REFERENCES rooms(id) ON DELETE SET NULL,

    -- Financial
    cost DECIMAL(10,2) DEFAULT 0.00, -- Cost per student
    registration_fee DECIMAL(10,2) DEFAULT 0.00,
    equipment_fee DECIMAL(10,2) DEFAULT 0.00,

    -- Requirements
    requirements TEXT[], -- Array of requirements (e.g., "Parent consent", "Medical clearance")
    equipment_needed TEXT[], -- Array of equipment students need
    uniform_required BOOLEAN DEFAULT FALSE,

    -- Contact & Communication
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    parent_info TEXT, -- Information for parents

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, full, cancelled, completed
    is_featured BOOLEAN DEFAULT FALSE, -- Featured on homepage
    registration_open BOOLEAN DEFAULT TRUE,

    -- Display
    photo_url VARCHAR(500),
    color VARCHAR(7), -- Hex color for UI

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID REFERENCES users(id),

    -- Constraints
    CONSTRAINT activities_status_check CHECK (status IN ('active', 'full', 'cancelled', 'completed')),
    CONSTRAINT activities_activity_type_check CHECK (activity_type IN ('sports', 'club', 'art', 'music', 'academic', 'other')),
    CONSTRAINT activities_cost_positive CHECK (cost >= 0),
    CONSTRAINT activities_registration_fee_positive CHECK (registration_fee >= 0),
    CONSTRAINT activities_equipment_fee_positive CHECK (equipment_fee >= 0),
    CONSTRAINT activities_max_participants_positive CHECK (max_participants IS NULL OR max_participants > 0),
    CONSTRAINT activities_min_participants_positive CHECK (min_participants IS NULL OR min_participants > 0),
    CONSTRAINT activities_unique_code UNIQUE (school_id, code, deleted_at)
);

-- Indexes
CREATE INDEX idx_activities_school_id ON activities(school_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_coordinator_id ON activities(coordinator_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_activity_type ON activities(activity_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_status ON activities(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_grade_levels ON activities USING GIN(grade_levels) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_deleted_at ON activities(deleted_at);
```

### Table: `activity_enrollments`

```sql
CREATE TABLE activity_enrollments (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign Keys
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,

    -- Enrollment Details
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, waitlisted, withdrawn, completed

    -- Payment
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, partial, paid, waived
    amount_paid DECIMAL(10,2) DEFAULT 0.00,
    payment_date DATE,

    -- Attendance
    attendance_count INT DEFAULT 0,
    total_sessions INT, -- Total sessions student should attend

    -- Performance
    performance_notes TEXT,
    achievements TEXT[], -- Array of achievements/awards

    -- Consent & Requirements
    parent_consent BOOLEAN DEFAULT FALSE,
    parent_consent_date DATE,
    medical_clearance BOOLEAN DEFAULT FALSE,
    emergency_contact_provided BOOLEAN DEFAULT FALSE,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    withdrawn_at TIMESTAMP WITH TIME ZONE,
    withdrawn_by UUID REFERENCES users(id),
    withdrawn_reason TEXT,

    -- Constraints
    CONSTRAINT enrollments_status_check CHECK (status IN ('active', 'waitlisted', 'withdrawn', 'completed')),
    CONSTRAINT enrollments_payment_status_check CHECK (payment_status IN ('pending', 'partial', 'paid', 'waived')),
    CONSTRAINT enrollments_amount_paid_positive CHECK (amount_paid >= 0),
    CONSTRAINT enrollments_unique_enrollment UNIQUE (activity_id, student_id)
);

-- Indexes
CREATE INDEX idx_enrollments_activity_id ON activity_enrollments(activity_id);
CREATE INDEX idx_enrollments_student_id ON activity_enrollments(student_id);
CREATE INDEX idx_enrollments_status ON activity_enrollments(status);
CREATE INDEX idx_enrollments_payment_status ON activity_enrollments(payment_status);
```

## Business Rules

### Activity Types
- **sports**: Athletic activities (basketball, soccer, track, etc.)
- **club**: Interest-based clubs (chess, robotics, debate, etc.)
- **art**: Visual and performing arts (painting, drawing, sculpture)
- **music**: Musical activities (band, choir, orchestra, guitar)
- **academic**: Academic enrichment (math club, science olympiad)
- **other**: Other extracurricular activities

### Enrollment Rules
- Students can only enroll in activities for their grade level
- Activities with max_participants will become "full" when reached
- Waitlist is created when activity is full
- Parent consent required for all enrollments
- Payment must be completed before participation
- Students can withdraw from activities
- Coordinators can add notes on student performance

### Status Workflow
- **active**: Activity is running and accepting registrations
- **full**: Activity reached max capacity (waitlist available)
- **cancelled**: Activity was cancelled
- **completed**: Activity season/term has ended

### Payment Handling
- Total cost = cost + registration_fee + equipment_fee
- Payment can be waived by administrator
- Partial payments allowed
- Payment tracking per student

### Validation Rules
- Name: Required, 1-255 characters
- Activity type: Required, must be valid type
- Grade levels: Required, at least one grade (1-7)
- Cost fields: Non-negative numbers
- Max participants: Positive integer if specified
- Coordinator must belong to same school
- Schedule must be valid JSONB format
- Dates: start_date must be before end_date

## API Endpoints

### Activity CRUD

#### 1. Create Activity
```http
POST /api/v1/activities?school_id={school_id}
Content-Type: application/json

{
  "name": "Basketball Team",
  "code": "BB-2024",
  "activity_type": "sports",
  "category": "basketball",
  "description": "Varsity basketball team for grades 5-7",
  "grade_levels": [5, 6, 7],
  "max_participants": 15,
  "min_participants": 10,
  "schedule": {
    "days": ["Monday", "Wednesday", "Friday"],
    "start_time": "15:30",
    "end_time": "17:00"
  },
  "start_date": "2024-11-01",
  "end_date": "2025-03-15",
  "location": "Gymnasium",
  "cost": 50.00,
  "registration_fee": 25.00,
  "coordinator_id": "uuid",
  "requirements": ["Parent consent", "Medical clearance"],
  "equipment_needed": ["Basketball shoes", "Athletic clothing"],
  "uniform_required": true,
  "contact_email": "coach@example.com",
  "color": "#FF5722"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Basketball Team",
  "status": "active",
  "enrollment_count": 0,
  ...
}
```

#### 2. List Activities (with filters)
```http
GET /api/v1/activities?school_id={school_id}&page=1&limit=50&activity_type=sports&status=active&grade_level=5

Response: 200 OK
{
  "activities": [...],
  "total": 25,
  "page": 1,
  "limit": 50,
  "total_pages": 1
}
```

#### 3. Get Activity by ID
```http
GET /api/v1/activities/{id}

Response: 200 OK
{
  "id": "uuid",
  "name": "Basketball Team",
  "enrollment_count": 12,
  "available_slots": 3,
  "enrollments": [...],
  ...
}
```

#### 4. Update Activity
```http
PUT /api/v1/activities/{id}
Content-Type: application/json

{
  "max_participants": 18,
  "status": "full"
}

Response: 200 OK
```

#### 5. Delete Activity
```http
DELETE /api/v1/activities/{id}

Response: 204 No Content
```

### Enrollment Management

#### 6. Enroll Student
```http
POST /api/v1/activities/{activity_id}/enroll
Content-Type: application/json

{
  "student_id": "uuid",
  "parent_consent": true,
  "medical_clearance": true,
  "emergency_contact_provided": true
}

Response: 201 Created
{
  "id": "uuid",
  "activity_id": "uuid",
  "student_id": "uuid",
  "status": "active",
  "enrollment_date": "2024-10-26"
}
```

#### 7. Withdraw Student
```http
POST /api/v1/activities/{activity_id}/withdraw/{student_id}
Content-Type: application/json

{
  "reason": "Student schedule conflict"
}

Response: 200 OK
```

#### 8. Get Activity Roster
```http
GET /api/v1/activities/{activity_id}/roster?status=active

Response: 200 OK
{
  "activity": {...},
  "enrollments": [
    {
      "id": "uuid",
      "student": {...},
      "status": "active",
      "enrollment_date": "2024-10-15",
      "payment_status": "paid"
    }
  ],
  "total_enrolled": 12,
  "available_slots": 3
}
```

#### 9. Get Student Activities
```http
GET /api/v1/activities/student/{student_id}?status=active

Response: 200 OK
[
  {
    "id": "uuid",
    "activity": {...},
    "status": "active",
    "enrollment_date": "2024-10-15"
  }
]
```

### Payment Management

#### 10. Record Payment
```http
POST /api/v1/activities/enrollments/{enrollment_id}/payment
Content-Type: application/json

{
  "amount": 75.00,
  "payment_date": "2024-10-26",
  "payment_status": "paid"
}

Response: 200 OK
```

#### 11. Waive Payment
```http
POST /api/v1/activities/enrollments/{enrollment_id}/waive-payment

Response: 200 OK
```

#### 12. Get Payment Status
```http
GET /api/v1/activities/{activity_id}/payments

Response: 200 OK
{
  "activity": {...},
  "payments": [
    {
      "student_id": "uuid",
      "student_name": "John Doe",
      "payment_status": "paid",
      "amount_paid": 75.00,
      "total_due": 75.00
    }
  ],
  "total_collected": 900.00,
  "total_outstanding": 150.00
}
```

### Query Endpoints

#### 13. Get Activities by Type
```http
GET /api/v1/activities/type/{activity_type}?school_id={school_id}

Response: 200 OK
[...]
```

#### 14. Get Activities by Coordinator
```http
GET /api/v1/activities/coordinator/{coordinator_id}?school_id={school_id}

Response: 200 OK
[...]
```

#### 15. Get Featured Activities
```http
GET /api/v1/activities/featured?school_id={school_id}

Response: 200 OK
[...]
```

#### 16. Search Activities
```http
GET /api/v1/activities/search?school_id={school_id}&query=basketball&page=1&limit=50

Response: 200 OK
{
  "activities": [...],
  "total": 3
}
```

### Statistics

#### 17. Get Activity Statistics
```http
GET /api/v1/activities/statistics?school_id={school_id}

Response: 200 OK
{
  "total_activities": 45,
  "by_type": {
    "sports": 15,
    "club": 12,
    "art": 8,
    "music": 6,
    "academic": 4
  },
  "by_status": {
    "active": 38,
    "full": 5,
    "cancelled": 2
  },
  "total_enrollments": 450,
  "average_enrollment_per_activity": 10,
  "total_revenue": 15750.00,
  "total_outstanding": 1250.00
}
```

## Frontend Components

### ActivityList Component
**Features:**
- Grid/list view toggle
- Filters: type, status, grade level, coordinator
- Search by name or description
- Quick enrollment actions
- Capacity indicators
- Payment status overview

### ActivityForm Component
**Sections:**
1. **Basic Information**
   - Name, code, type, category
   - Description
   - Coordinator

2. **Eligibility & Capacity**
   - Grade levels (multi-select)
   - Max/min participants
   - Requirements checklist

3. **Schedule & Location**
   - Days of week
   - Start/end times
   - Start/end dates
   - Location/room

4. **Financial**
   - Activity cost
   - Registration fee
   - Equipment fee

5. **Requirements**
   - Equipment needed (dynamic list)
   - Uniform required checkbox
   - Parent information

6. **Settings**
   - Status
   - Registration open/closed
   - Featured toggle
   - Color picker
   - Photo upload

### ActivityRoster Component
**Features:**
- Student list with photos
- Payment status indicators
- Attendance tracking
- Performance notes
- Quick withdrawal action
- Export roster to PDF/CSV

### ActivityEnrollment Component (Student/Parent View)
**Features:**
- Browse available activities
- Filter by type, grade, schedule
- View activity details
- Enrollment form
- Payment information
- Consent forms
- Activity calendar

## TypeScript Types

```typescript
export type ActivityType = 'sports' | 'club' | 'art' | 'music' | 'academic' | 'other';
export type ActivityStatus = 'active' | 'full' | 'cancelled' | 'completed';
export type EnrollmentStatus = 'active' | 'waitlisted' | 'withdrawn' | 'completed';
export type PaymentStatus = 'pending' | 'partial' | 'paid' | 'waived';

export interface ActivitySchedule {
  days: string[]; // ["Monday", "Wednesday", "Friday"]
  start_time: string; // "15:30"
  end_time: string; // "17:00"
}

export interface Activity {
  id: string;
  school_id: string;
  coordinator_id: string | null;
  name: string;
  code: string | null;
  activity_type: ActivityType;
  category: string | null;
  description: string | null;
  grade_levels: number[];
  max_participants: number | null;
  min_participants: number | null;
  schedule: ActivitySchedule;
  start_date: string | null;
  end_date: string | null;
  location: string | null;
  room_id: string | null;
  cost: number;
  registration_fee: number;
  equipment_fee: number;
  requirements: string[];
  equipment_needed: string[];
  uniform_required: boolean;
  contact_email: string | null;
  contact_phone: string | null;
  parent_info: string | null;
  status: ActivityStatus;
  is_featured: boolean;
  registration_open: boolean;
  photo_url: string | null;
  color: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;

  // Computed fields
  coordinator_name?: string;
  enrollment_count?: number;
  available_slots?: number;
  total_cost?: number;
}

export interface ActivityEnrollment {
  id: string;
  activity_id: string;
  student_id: string;
  enrollment_date: string;
  status: EnrollmentStatus;
  payment_status: PaymentStatus;
  amount_paid: number;
  payment_date: string | null;
  attendance_count: number;
  total_sessions: number | null;
  performance_notes: string | null;
  achievements: string[];
  parent_consent: boolean;
  parent_consent_date: string | null;
  medical_clearance: boolean;
  emergency_contact_provided: boolean;
  created_at: string;
  updated_at: string;
  withdrawn_at: string | null;
  withdrawn_reason: string | null;

  // Computed fields
  student?: any;
  activity?: Activity;
  amount_due?: number;
}

export interface ActivityStatistics {
  total_activities: number;
  by_type: Record<ActivityType, number>;
  by_status: Record<ActivityStatus, number>;
  total_enrollments: number;
  average_enrollment_per_activity: number;
  total_revenue: number;
  total_outstanding: number;
}
```

## Sample Data

```javascript
const sampleActivities = [
  {
    name: "Basketball Team",
    code: "BB-2024",
    activity_type: "sports",
    category: "basketball",
    description: "Competitive basketball team for grades 5-7. Practice twice a week with games on weekends.",
    grade_levels: [5, 6, 7],
    max_participants: 15,
    min_participants: 10,
    schedule: {
      days: ["Monday", "Wednesday"],
      start_time: "15:30",
      end_time: "17:00"
    },
    start_date: "2024-11-01",
    end_date: "2025-03-15",
    location: "Main Gymnasium",
    cost: 50.00,
    registration_fee: 25.00,
    equipment_fee: 0.00,
    requirements: ["Parent consent", "Medical clearance", "Physical exam"],
    equipment_needed: ["Basketball shoes", "Athletic clothing", "Water bottle"],
    uniform_required: true,
    contact_email: "coach.basketball@example.com",
    contact_phone: "+1234567890",
    parent_info: "Parents are encouraged to attend games. Game schedule will be sent monthly.",
    status: "active",
    registration_open: true,
    color: "#FF5722"
  },
  {
    name: "Chess Club",
    code: "CHESS-2024",
    activity_type: "club",
    category: "chess",
    description: "Learn chess strategies and compete in tournaments. All skill levels welcome!",
    grade_levels: [3, 4, 5, 6, 7],
    max_participants: 20,
    schedule: {
      days: ["Tuesday", "Thursday"],
      start_time: "15:00",
      end_time: "16:00"
    },
    start_date: "2024-11-01",
    end_date: "2025-05-30",
    location: "Library",
    cost: 0.00,
    registration_fee: 10.00,
    equipment_fee: 0.00,
    requirements: ["Parent consent"],
    equipment_needed: [],
    uniform_required: false,
    contact_email: "chess.club@example.com",
    parent_info: "Club participates in 3 regional tournaments per year.",
    status: "active",
    registration_open: true,
    color: "#9C27B0"
  },
  {
    name: "Art Studio",
    code: "ART-2024",
    activity_type: "art",
    category: "painting",
    description: "Explore various art mediums including painting, drawing, and sculpture.",
    grade_levels: [1, 2, 3, 4],
    max_participants: 12,
    schedule: {
      days: ["Friday"],
      start_time: "15:30",
      end_time: "17:00"
    },
    start_date: "2024-11-01",
    end_date: "2025-04-30",
    location: "Art Room 101",
    cost: 35.00,
    registration_fee: 15.00,
    equipment_fee: 20.00,
    requirements: ["Parent consent"],
    equipment_needed: ["Smock or old t-shirt"],
    uniform_required: false,
    contact_email: "art.teacher@example.com",
    parent_info: "Supply fee covers all art materials. Student work will be displayed at annual art show.",
    status: "active",
    registration_open: true,
    is_featured: true,
    color: "#E91E63"
  },
  {
    name: "Choir",
    code: "CHOIR-2024",
    activity_type: "music",
    category: "vocal",
    description: "School choir performing classical and contemporary music. Two concerts per year.",
    grade_levels: [4, 5, 6, 7],
    max_participants: 30,
    schedule: {
      days: ["Monday", "Wednesday"],
      start_time: "16:00",
      end_time: "17:00"
    },
    start_date: "2024-11-01",
    end_date: "2025-05-30",
    location: "Music Room",
    cost: 0.00,
    registration_fee: 0.00,
    equipment_fee: 25.00,
    requirements: ["Parent consent", "Audition"],
    equipment_needed: ["Black shoes", "Performance attire"],
    uniform_required: true,
    contact_email: "music.director@example.com",
    parent_info: "Uniforms provided. Parents needed for concert chaperoning.",
    status: "active",
    registration_open: true,
    color: "#2196F3"
  },
  {
    name: "Math Olympiad",
    code: "MATH-OLY-2024",
    activity_type: "academic",
    category: "mathematics",
    description: "Prepare for regional and state math competitions. Advanced problem-solving focus.",
    grade_levels: [5, 6, 7],
    max_participants: 15,
    schedule: {
      days: ["Thursday"],
      start_time: "15:00",
      end_time: "16:30"
    },
    start_date: "2024-11-01",
    end_date: "2025-04-15",
    location: "Room 205",
    cost: 20.00,
    registration_fee: 10.00,
    equipment_fee: 0.00,
    requirements: ["Parent consent", "Teacher recommendation"],
    equipment_needed: ["Calculator", "Notebook"],
    uniform_required: false,
    contact_email: "math.olympiad@example.com",
    parent_info: "Students will compete in 4 competitions. Transportation provided.",
    status: "active",
    registration_open: true,
    color: "#4CAF50"
  }
];
```

## Implementation Checklist

### Backend
- [ ] Create migration SQL file
- [ ] Apply migration to database
- [ ] Create Activity and ActivityEnrollment ORM models
- [ ] Create ActivityRepository with 17+ methods
- [ ] Create ActivityService with business logic
- [ ] Create Pydantic schemas
- [ ] Create ActivityController with 17 endpoints
- [ ] Register routes in main.py
- [ ] Test all endpoints manually
- [ ] Commit backend implementation

### Frontend
- [ ] Create TypeScript types
- [ ] Create ActivityService API client
- [ ] Create ActivityStore Pinia store
- [ ] Create ActivityList component
- [ ] Create ActivityForm component
- [ ] Create ActivityRoster component
- [ ] Create ActivityEnrollment component
- [ ] Add routing
- [ ] Add navigation
- [ ] Test and commit frontend

### Testing
- [ ] Backend unit tests
- [ ] API integration tests
- [ ] Frontend E2E tests
- [ ] CRUD operations verification
- [ ] Enrollment workflow testing
- [ ] Payment tracking testing
- [ ] Multi-tenancy verification

## Notes
- Activities are school-specific with grade-level restrictions
- Payment tracking is important for financial reporting
- Parent consent required for all activity enrollments
- Coordinators can be any user with appropriate permissions
- Waitlist functionality when activity reaches capacity
- Activity completion triggers at end_date
- Statistics help administrators track program participation and revenue
