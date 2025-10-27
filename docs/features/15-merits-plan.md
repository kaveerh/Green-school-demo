# Feature #15: Merits (Merit/Reward System)

## Overview
The Merits system provides a positive behavior reinforcement mechanism for recognizing and rewarding student achievements, good behavior, and participation. Teachers and administrators can award merits for academic excellence, positive behavior, leadership, participation, and other accomplishments. The system tracks individual and class-level achievements, supports merit categories, and provides analytics for monitoring student engagement and motivation.

## Priority
**Priority 15 of 15** - Reward and recognition system

## Dependencies
- **Users** (Feature #1) - Award tracking
- **Schools** (Feature #2) - Multi-tenancy
- **Teachers** (Feature #3) - Merit awarding
- **Students** (Feature #4) - Merit recipients
- **Classes** (Feature #8) - Class-level tracking

## Use Cases

### UC15.1: Award Merit
**Actor**: Teacher, Administrator
**Description**: Award merit points to a student for specific achievements or behavior
**Preconditions**: Student exists, user has permission
**Postconditions**: Merit record created, student's total updated

**Flow**:
1. Teacher selects student
2. Chooses merit category (academic, behavior, participation, leadership, other)
3. Enters merit points (1-10)
4. Adds description/reason
5. Optionally links to class or subject
6. System records merit with timestamp
7. Student's total merit points updated
8. Parent notification sent (optional)

### UC15.2: View Student Merits
**Actor**: Teacher, Administrator, Parent, Student
**Description**: View merit history for a student
**Preconditions**: Student exists, appropriate permissions
**Postconditions**: Merit history displayed

**Flow**:
1. User views student profile
2. System displays merit history (chronological)
3. Shows total merits by category
4. Displays recent awards with details
5. Shows ranking within class/grade (optional)

### UC15.3: Award Class Merit
**Actor**: Teacher, Administrator
**Description**: Award merits to entire class
**Preconditions**: Class exists, students enrolled
**Postconditions**: Merit records created for all students

**Flow**:
1. Teacher selects class
2. Chooses merit category and points
3. Enters reason for class award
4. System creates individual merit records for each student
5. Updates all student totals

### UC15.4: Generate Merit Reports
**Actor**: Teacher, Administrator
**Description**: View merit statistics and leaderboards
**Preconditions**: Merit records exist
**Postconditions**: Report generated

**Flow**:
1. User selects report type (student, class, grade, quarter)
2. Applies filters (date range, category, grade level)
3. System generates statistics
4. Displays leaderboards and trends
5. Exports to PDF/CSV (optional)

### UC15.5: Revoke Merit
**Actor**: Administrator
**Description**: Remove incorrectly awarded merit
**Preconditions**: Merit exists, admin permissions
**Postconditions**: Merit soft-deleted, totals recalculated

**Flow**:
1. Administrator finds merit record
2. Provides reason for revocation
3. System soft-deletes merit
4. Recalculates student total
5. Logs action in audit trail

## Database Schema

### Table: merits

```sql
CREATE TABLE IF NOT EXISTS merits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    awarded_by_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    subject_id UUID REFERENCES subjects(id) ON DELETE SET NULL,

    -- Merit Details
    category VARCHAR(50) NOT NULL,  -- 'academic', 'behavior', 'participation', 'leadership', 'attendance', 'other'
    points INTEGER NOT NULL,  -- 1-10
    reason TEXT NOT NULL,  -- Description of why merit was awarded

    -- Context
    quarter VARCHAR(10),  -- 'Q1', 'Q2', 'Q3', 'Q4'
    academic_year VARCHAR(20),  -- '2024-2025'
    awarded_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Metadata
    is_class_award BOOLEAN DEFAULT FALSE,  -- Was this part of a class-wide award
    batch_id UUID,  -- Groups merits awarded together

    -- Audit Trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_by UUID REFERENCES users(id),

    -- Constraints
    CONSTRAINT chk_merits_category CHECK (category IN ('academic', 'behavior', 'participation', 'leadership', 'attendance', 'other')),
    CONSTRAINT chk_merits_points CHECK (points >= 1 AND points <= 10),
    CONSTRAINT chk_merits_quarter CHECK (quarter IS NULL OR quarter IN ('Q1', 'Q2', 'Q3', 'Q4'))
);

-- Indexes
CREATE INDEX idx_merits_school_id ON merits(school_id);
CREATE INDEX idx_merits_student_id ON merits(student_id);
CREATE INDEX idx_merits_awarded_by_id ON merits(awarded_by_id);
CREATE INDEX idx_merits_class_id ON merits(class_id);
CREATE INDEX idx_merits_category ON merits(category);
CREATE INDEX idx_merits_awarded_date ON merits(awarded_date);
CREATE INDEX idx_merits_quarter ON merits(quarter);
CREATE INDEX idx_merits_deleted_at ON merits(deleted_at);
CREATE INDEX idx_merits_batch_id ON merits(batch_id) WHERE batch_id IS NOT NULL;

-- RLS Policy
ALTER TABLE merits ENABLE ROW LEVEL SECURITY;

CREATE POLICY merits_school_isolation ON merits
    USING (school_id = current_setting('app.current_school_id')::UUID);
```

### Computed Properties
- `student_total_merits` - Total merit points for a student
- `student_merits_by_category` - Breakdown by category
- `class_average_merits` - Average merits per student in class
- `grade_level_ranking` - Student's rank within grade

## API Endpoints

### Merit CRUD Endpoints

#### POST /api/v1/merits
**Award merit to a student**
- Request Body: `{ student_id, category, points, reason, class_id?, subject_id?, quarter?, awarded_date? }`
- Query Params: `awarded_by_id` (required)
- Response: Merit object
- Validation: Valid category, points 1-10, student exists

#### POST /api/v1/merits/batch
**Award merits to multiple students (class award)**
- Request Body: `{ student_ids[], category, points, reason, class_id?, subject_id?, quarter? }`
- Query Params: `awarded_by_id` (required)
- Response: Array of merit objects
- Creates batch_id to group awards

#### GET /api/v1/merits
**List all merits with filters**
- Query Params: `school_id` (required), `student_id?`, `class_id?`, `category?`, `quarter?`, `awarded_by_id?`, `start_date?`, `end_date?`, `page`, `limit`
- Response: Paginated merit list
- Supports filtering by multiple criteria

#### GET /api/v1/merits/{id}
**Get merit by ID**
- Response: Merit object with full details

#### PUT /api/v1/merits/{id}
**Update merit** (limited fields)
- Request Body: `{ points?, reason?, category? }`
- Query Params: `updated_by_id` (required)
- Response: Updated merit object

#### DELETE /api/v1/merits/{id}
**Revoke merit (soft delete)**
- Query Params: `deleted_by_id` (required), `reason?`
- Response: 204 No Content

### Query Endpoints

#### GET /api/v1/merits/student/{student_id}
**Get all merits for a student**
- Query Params: `quarter?`, `category?`, `page`, `limit`
- Response: Paginated merit list with student totals

#### GET /api/v1/merits/student/{student_id}/summary
**Get merit summary for a student**
- Response: `{ total_points, by_category, by_quarter, recent_merits[], ranking }`

#### GET /api/v1/merits/class/{class_id}
**Get all merits for a class**
- Query Params: `quarter?`, `category?`, `page`, `limit`
- Response: Paginated merit list

#### GET /api/v1/merits/class/{class_id}/summary
**Get class merit statistics**
- Response: `{ total_points, average_per_student, by_category, top_students[], distribution }`

#### GET /api/v1/merits/teacher/{teacher_id}
**Get merits awarded by a teacher**
- Query Params: `quarter?`, `page`, `limit`
- Response: Paginated merit list

#### GET /api/v1/merits/leaderboard
**Get merit leaderboard**
- Query Params: `school_id` (required), `grade_level?`, `quarter?`, `limit` (default 20)
- Response: Array of student rankings with total merits

#### GET /api/v1/merits/statistics/summary
**Get school-wide merit statistics**
- Query Params: `school_id` (required), `quarter?`, `grade_level?`
- Response: Comprehensive statistics
  - Total merits awarded
  - By category breakdown
  - By quarter breakdown
  - Average per student
  - Most active teachers
  - Trending categories

## Business Rules

### Merit Points
1. Merit points range from 1-10
2. Typical awards:
   - Minor achievement/good behavior: 1-2 points
   - Moderate achievement: 3-5 points
   - Significant achievement: 6-8 points
   - Exceptional achievement: 9-10 points

### Merit Categories
1. **Academic** - Academic excellence, improvement, test scores
2. **Behavior** - Good conduct, helping others, respect
3. **Participation** - Class engagement, volunteering, clubs
4. **Leadership** - Taking initiative, mentoring, responsibility
5. **Attendance** - Perfect attendance, punctuality
6. **Other** - Special achievements not in other categories

### Permissions
- **Teachers** - Award merits to students in their classes
- **Administrators** - Award merits to any student, revoke merits
- **Students** - View own merits only
- **Parents** - View their children's merits only

### Merit Awards
1. Teachers can award merits daily
2. No limit on merits per day (prevents gaming)
3. Merits are final once awarded (soft delete for corrections)
4. Class awards create individual merit records for each student
5. Batch awards grouped by batch_id

### Reporting & Recognition
1. Leaderboards updated in real-time
2. Rankings can be by class, grade, or school-wide
3. Quarter-based tracking for term recognition
4. Annual totals for year-end awards
5. Export capability for certificates/reports

### Data Retention
1. Merit records maintained permanently for historical tracking
2. Soft delete for administrative corrections
3. Full audit trail of all merit activities
4. GDPR compliance - merits deleted with student data

## Validation Rules

### Award Merit
- Student must exist and be active
- Awarder must have permission
- Points must be 1-10
- Category must be valid
- Reason required (min 10 characters)
- If class_id provided, student must be enrolled
- Quarter must be valid if provided

### Batch Awards
- At least one student_id required
- All students must exist and be active
- Same validations as single award
- Batch_id auto-generated

### Revoke Merit
- Only administrators can revoke
- Reason for revocation logged
- Student totals recalculated

## Analytics & Reports

### Student Analytics
- Total merit points (all-time and by quarter)
- Merit distribution by category
- Trend over time (line chart)
- Comparison to class average
- Ranking within grade level

### Class Analytics
- Total class merits
- Average per student
- Top performers
- Category distribution
- Comparison to other classes

### School Analytics
- Total merits awarded
- Most active categories
- Most engaged teachers
- Grade-level comparisons
- Quarter-over-quarter trends

## Implementation Phases

### Phase 1: Core Merit System (MVP)
- Merit CRUD operations
- Single student awards
- Basic filtering and search
- Student merit history
- Simple statistics

### Phase 2: Advanced Features
- Batch/class awards
- Leaderboards and rankings
- Advanced analytics and reports
- Export functionality
- Parent notifications
- Merit milestones/badges

### Phase 3: Gamification
- Achievement badges
- Merit tiers/levels
- Rewards catalog
- Redemption system
- Team competitions

## Frontend Components

### Merit Award Modal
- Student selector
- Category dropdown
- Points slider (1-10)
- Reason text area
- Class/subject association
- Quick award presets

### Student Merit Card
- Total points display
- Category breakdown (pie chart)
- Recent awards list
- Progress towards next milestone
- Ranking badge

### Merit Leaderboard
- Top students list
- Filter by grade/class/quarter
- Category-specific leaderboards
- Visual rankings with avatars

### Merit History Table
- Chronological list
- Filter by category/quarter
- Teacher who awarded
- Points and reason
- Export options

### Class Merit Dashboard
- Class statistics
- Student distribution chart
- Recent class awards
- Top students in class
- Award class button

## Integration Points

### Students Module
- Display total merits on student profile
- Merit history tab
- Merit trends chart

### Classes Module
- Class merit statistics
- Quick award to class
- Top students widget

### Teachers Module
- Merits awarded history
- Quick award button
- Recognition statistics

### Reports Module
- Merit analytics dashboard
- Leaderboard reports
- Recognition certificates
- Parent reports

## Sample Data
5 sample merit records:
1. Academic excellence - Math test (10 points)
2. Helping classmate - Good behavior (5 points)
3. Perfect attendance - Week award (3 points)
4. Class participation - Active engagement (4 points)
5. Leadership - Group project leader (7 points)

## Testing Checklist
- [ ] Award merit to single student
- [ ] Award merits to entire class (batch)
- [ ] View student merit history
- [ ] Calculate student totals correctly
- [ ] Generate leaderboard rankings
- [ ] Filter by category and quarter
- [ ] Revoke merit (admin only)
- [ ] Calculate class statistics
- [ ] Test permission boundaries
- [ ] Verify multi-tenancy isolation

## Success Metrics
- Merits awarded per day/week
- Teacher participation rate
- Student engagement correlation
- Merit distribution balance
- Parent/student satisfaction
- Behavioral improvement correlation

---

**Status**: Ready for Implementation
**Last Updated**: 2025-10-26
