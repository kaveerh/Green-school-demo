# Database Schema Overview
**Version**: 1.0
**Last Updated**: 2025-10-13
**Database**: PostgreSQL 14+

## Overview
Complete database schema for Green School Management System supporting 15 core features with multi-tenant architecture and GDPR compliance.

## Architecture Principles

### Multi-Tenant Design
- All tables include `school_id UUID NOT NULL REFERENCES schools(id)`
- Row Level Security (RLS) policies enforce tenant isolation
- Queries automatically filtered by school context
- No cross-tenant data access possible

### Audit Trail
All tables include standard audit fields:
```sql
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW(),
created_by UUID REFERENCES users(id),
updated_by UUID REFERENCES users(id),
deleted_at TIMESTAMP,           -- Soft delete
deleted_by UUID REFERENCES users(id)
```

### Primary Keys
- All tables use UUID primary keys: `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
- UUIDs provide distributed system compatibility
- No auto-incrementing integers for security

### Naming Conventions
- Tables: Plural lowercase with underscores (e.g., `student_classes`)
- Columns: Lowercase with underscores (e.g., `first_name`)
- Foreign Keys: `{referenced_table_singular}_id` (e.g., `school_id`, `user_id`)
- Indexes: `idx_{table}_{column(s)}` (e.g., `idx_users_email`)
- Constraints: `chk_{table}_{column}` (e.g., `chk_users_persona`)

## Entity Relationship Diagram (Text)

```
┌──────────┐
│ schools  │
└────┬─────┘
     │
     ├─────────────────┬────────────────┬─────────────────┐
     │                 │                │                 │
┌────▼─────┐     ┌────▼─────┐    ┌────▼─────┐     ┌────▼─────┐
│  users   │     │ subjects │    │  rooms   │     │  events  │
└────┬─────┘     └────┬─────┘    └────┬─────┘     └──────────┘
     │                 │                │
     ├────────┬────────┼────────┬───────┤
     │        │        │        │       │
┌────▼────┐┌─▼──────┐┌▼──────┐┌▼─────┐│
│teachers ││students││parents││vendors││
└────┬────┘└───┬────┘└───┬───┘└───────┘│
     │         │          │             │
     │    ┌────▼──────────▼─┐           │
     │    │parent_student_  │           │
     │    │ relationships   │           │
     │    └─────────────────┘           │
     │         │                        │
     └────┬────┴────┬───────────────────┘
          │         │
     ┌────▼─────────▼───┐
     │     classes      │
     └────┬─────────────┘
          │
     ┌────┼─────┬──────────┬────────────┐
     │    │     │          │            │
┌────▼┐┌──▼───┐┌▼────────┐┌▼──────────┐│
│less-││asmts ││attend-  ││student_   ││
│ons  ││      ││ance     ││classes    ││
└─────┘└──┬───┘└─────────┘└───────────┘│
          │                             │
     ┌────▼─────────────────┐           │
     │ assessment_results   │           │
     └──────────────────────┘           │
                                        │
┌────────────┐  ┌──────────────┐      ┌▼──────────┐
│activities  │  │    merits    │      │ activity_ │
│            │  │              │      │enrollments│
└────────────┘  └──────────────┘      └───────────┘
```

## Core Tables (14 Total)

### 1. schools
**Purpose**: Multi-tenant foundation
**Relationships**: One-to-many with all other tables
**Key Fields**: name, slug, logo_url, principal_id, hod_id

### 2. users
**Purpose**: Authentication and authorization
**Relationships**:
- References: schools
- Referenced by: teachers, students, parents, vendors (via user_id)
**Key Fields**: email, persona, status, keycloak_id

### 3. teachers
**Purpose**: Teacher profiles and assignments
**Relationships**:
- References: users, schools
- Referenced by: classes, lessons, assessments
**Key Fields**: employee_id, grades[], specializations[]

### 4. students
**Purpose**: Student profiles and academic tracking
**Relationships**:
- References: users, schools
- Referenced by: parent_student_relationships, student_classes, attendance, merits
**Key Fields**: student_id, grade_level, date_of_birth

### 5. parents
**Purpose**: Parent profiles
**Relationships**:
- References: users, schools
- Referenced by: parent_student_relationships
**Key Fields**: occupation, preferred_contact_method

### 6. parent_student_relationships
**Purpose**: Link parents to their children
**Relationships**:
- References: users (parent_id), students (student_id)
**Key Fields**: relationship_type, is_primary_contact, has_pickup_permission

### 7. subjects
**Purpose**: Curriculum subjects
**Relationships**:
- References: schools
- Referenced by: classes
**Key Fields**: code, grade_levels[], is_required

### 8. rooms
**Purpose**: Facility management
**Relationships**:
- References: schools, users (owner_id)
- Referenced by: classes, events
**Key Fields**: room_number, room_type, capacity, equipment[]

### 9. classes
**Purpose**: Class creation combining teacher + subject + students
**Relationships**:
- References: schools, subjects, teachers, rooms
- Referenced by: student_classes, lessons, assessments, attendance
**Key Fields**: code, grade_level, quarter, max_students, schedule

### 10. student_classes
**Purpose**: Student enrollment in classes
**Relationships**:
- References: students, classes
**Key Fields**: enrollment_date, status, final_grade

### 11. lessons
**Purpose**: Lesson planning
**Relationships**:
- References: schools, classes, teachers
**Key Fields**: title, quarter, objectives[], materials[], curriculum_standards[]

### 12. assessments
**Purpose**: Tests, quizzes, projects
**Relationships**:
- References: schools, classes, teachers
- Referenced by: assessment_results
**Key Fields**: assessment_type, quarter, total_points, rubric

### 13. assessment_results
**Purpose**: Student grades
**Relationships**:
- References: assessments, students, users (graded_by)
**Key Fields**: score, grade, feedback, status

### 14. attendance
**Purpose**: Daily attendance tracking
**Relationships**:
- References: schools, students, classes, users (recorded_by)
**Key Fields**: attendance_date, status, check_in_time, parent_notified

### Additional Tables

### events
**Purpose**: School calendar events
**Relationships**:
- References: schools, rooms, users (organizer_id), vendors
- Referenced by: event_attendees
**Key Fields**: event_type, start_date, end_date, requires_rsvp

### event_attendees
**Purpose**: Event RSVP tracking
**Relationships**:
- References: events, users
**Key Fields**: rsvp_status, checked_in

### activities
**Purpose**: Extracurricular activities
**Relationships**:
- References: schools, users (coordinator_id)
- Referenced by: activity_enrollments
**Key Fields**: activity_type, grade_levels[], schedule

### activity_enrollments
**Purpose**: Student activity participation
**Relationships**:
- References: activities, students
**Key Fields**: enrollment_date, status

### vendors
**Purpose**: Third-party vendors
**Relationships**:
- References: schools, users
- Referenced by: events
**Key Fields**: company_name, vendor_type, contact_info

### merits
**Purpose**: Student reward system
**Relationships**:
- References: schools, students, users (awarded_by), classes
**Key Fields**: merit_type, points, quarter

### merit_milestones
**Purpose**: Merit achievement levels
**Relationships**:
- References: schools
**Key Fields**: name, points_required, reward_description

## Data Types Reference

### Common Types
- **UUID**: Universally unique identifier
- **VARCHAR(n)**: Variable character string with max length
- **TEXT**: Unlimited text
- **INT**: Integer
- **DECIMAL(p,s)**: Decimal with precision and scale
- **BOOLEAN**: True/false
- **DATE**: Date only (YYYY-MM-DD)
- **TIME**: Time only (HH:MM:SS)
- **TIMESTAMP**: Date and time
- **JSONB**: JSON binary format (indexed)
- **Array Types**: INT[], TEXT[], etc.

### Custom Enums (via CHECK constraints)
- **persona**: administrator, teacher, student, parent, vendor
- **user_status**: active, inactive, suspended
- **student_status**: enrolled, graduated, transferred, withdrawn
- **attendance_status**: present, absent, tardy, excused, sick
- **assessment_type**: quiz, test, project, oral, homework
- **quarter**: Q1, Q2, Q3, Q4
- **room_type**: classroom, lab, gym, library, office, cafeteria
- **event_type**: field_trip, assembly, parent_meeting, sports, festival
- **activity_type**: sports, club, art, music
- **vendor_type**: supplies, food, transport, services
- **merit_type**: academic, behavior, participation, leadership

## Index Strategy

### Primary Indexes (Automatic)
- Primary key indexes on all `id` columns
- Unique indexes on UNIQUE constraints

### Foreign Key Indexes
```sql
-- All foreign keys should have indexes
CREATE INDEX idx_{table}_{fk_column} ON {table}({fk_column});
```

### Multi-Tenant Indexes (Critical)
```sql
-- All tables with school_id
CREATE INDEX idx_{table}_school_id ON {table}(school_id);
```

### Query Performance Indexes
```sql
-- Email lookup
CREATE INDEX idx_users_email ON users(email);

-- Status filtering
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_students_status ON students(status);

-- Date range queries
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_lessons_date ON lessons(lesson_date);
CREATE INDEX idx_assessments_date ON assessments(assessment_date);

-- Composite indexes for common queries
CREATE INDEX idx_students_school_grade ON students(school_id, grade_level);
CREATE INDEX idx_classes_school_quarter ON classes(school_id, quarter);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, attendance_date);
```

### Soft Delete Indexes
```sql
-- Filter out deleted records efficiently
CREATE INDEX idx_{table}_deleted_at ON {table}(deleted_at);
```

## Constraints

### Foreign Key Constraints
- All foreign keys use `ON DELETE CASCADE` or `ON DELETE SET NULL` appropriately
- Critical relationships use CASCADE (e.g., school deletion cascades to all school data)
- Optional relationships use SET NULL (e.g., room deletion sets class.room_id to NULL)

### Check Constraints
```sql
-- Validate enum values
ALTER TABLE users ADD CONSTRAINT chk_users_persona
  CHECK (persona IN ('administrator', 'teacher', 'student', 'parent', 'vendor'));

-- Validate ranges
ALTER TABLE students ADD CONSTRAINT chk_students_grade_level
  CHECK (grade_level BETWEEN 1 AND 7);

-- Validate positive numbers
ALTER TABLE assessments ADD CONSTRAINT chk_assessments_points
  CHECK (total_points > 0);
```

### Unique Constraints
```sql
-- Prevent duplicates
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
ALTER TABLE schools ADD CONSTRAINT uq_schools_slug UNIQUE (slug);
ALTER TABLE classes ADD CONSTRAINT uq_classes_code UNIQUE (code);

-- Composite unique constraints
ALTER TABLE parent_student_relationships
  ADD CONSTRAINT uq_parent_student UNIQUE (parent_id, student_id);
```

## Row Level Security (RLS) Policies

### Enable RLS on All Tables
```sql
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
```

### Standard Policy Pattern
```sql
-- Allow users to see only their school's data
CREATE POLICY {table}_school_isolation ON {table_name}
  USING (school_id = current_setting('app.current_school_id')::UUID);

-- Allow full access to system admins
CREATE POLICY {table}_admin_all ON {table_name}
  USING (current_setting('app.user_role') = 'system_admin');
```

### User-Specific Policies
```sql
-- Students can only see their own data
CREATE POLICY students_view_self ON students
  USING (user_id = current_setting('app.current_user_id')::UUID);

-- Teachers can see students in their classes
CREATE POLICY students_teachers_view ON students
  USING (
    id IN (
      SELECT DISTINCT sc.student_id
      FROM student_classes sc
      JOIN classes c ON sc.class_id = c.id
      WHERE c.teacher_id = current_setting('app.current_teacher_id')::UUID
    )
  );

-- Parents can see their children
CREATE POLICY students_parents_view ON students
  USING (
    id IN (
      SELECT student_id
      FROM parent_student_relationships
      WHERE parent_id = current_setting('app.current_user_id')::UUID
    )
  );
```

## Migration Strategy

### File Naming Convention
```
migrations/
├── 001_create_schools_and_users.sql
├── 002_create_teachers_students_parents.sql
├── 003_create_subjects_and_rooms.sql
├── 004_create_classes_and_enrollments.sql
├── 005_create_lessons_and_assessments.sql
├── 006_create_attendance.sql
├── 007_create_events_and_activities.sql
├── 008_create_vendors_and_merits.sql
├── 009_create_indexes.sql
├── 010_create_rls_policies.sql
└── 999_seed_initial_data.sql
```

### Migration Template
```sql
-- Migration: XXX_description.sql
-- Created: YYYY-MM-DD
-- Description: Brief description of changes

BEGIN;

-- Create tables
CREATE TABLE IF NOT EXISTS {table_name} (
  -- columns here
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_{name} ON {table}({columns});

-- Add constraints
ALTER TABLE {table} ADD CONSTRAINT {name} ...;

COMMIT;

-- Rollback (save in separate file: XXX_rollback.sql)
-- DROP TABLE IF EXISTS {table_name} CASCADE;
```

## Seed Data Requirements

Each feature must include seed data script creating minimum 5 realistic records:

### Example: Seed Users
```sql
-- seeds/001_seed_users.sql
INSERT INTO users (school_id, email, first_name, last_name, persona, status) VALUES
  ('{school_id}', 'admin@greenschool.edu', 'Alice', 'Admin', 'administrator', 'active'),
  ('{school_id}', 'john.teacher@greenschool.edu', 'John', 'Smith', 'teacher', 'active'),
  ('{school_id}', 'jane.teacher@greenschool.edu', 'Jane', 'Doe', 'teacher', 'active'),
  ('{school_id}', 'bob.student@greenschool.edu', 'Bob', 'Johnson', 'student', 'active'),
  ('{school_id}', 'mary.parent@greenschool.edu', 'Mary', 'Johnson', 'parent', 'active');
```

## Performance Optimization

### Query Optimization
- Use indexes for all WHERE, JOIN, ORDER BY columns
- Avoid SELECT * - specify only needed columns
- Use LIMIT for pagination
- Use EXPLAIN ANALYZE to profile slow queries

### Connection Pooling
- Minimum 10 connections
- Maximum 100 connections
- Connection timeout: 30 seconds
- Idle timeout: 600 seconds

### Partitioning (Future)
For high-volume tables, consider partitioning:
- `attendance` - Partition by month
- `assessment_results` - Partition by quarter
- `merits` - Partition by quarter

## Backup Strategy

### Daily Backups
```bash
pg_dump -h localhost -U postgres greenschool > backup_$(date +%Y%m%d).sql
```

### Point-in-Time Recovery
Enable WAL archiving for point-in-time recovery:
```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

## Database Maintenance

### Regular Tasks
```sql
-- Vacuum and analyze (weekly)
VACUUM ANALYZE;

-- Reindex (monthly)
REINDEX DATABASE greenschool;

-- Update statistics (daily)
ANALYZE;
```

### Monitoring Queries
```sql
-- Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Check slow queries
SELECT
  query,
  calls,
  mean_exec_time,
  max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

## Security Best Practices

### Connection Security
- Use SSL/TLS for all connections
- Encrypt data at rest
- Strong password policies
- Regular security audits

### SQL Injection Prevention
- Use parameterized queries (ORM handles this)
- Never concatenate user input into SQL
- Validate all input at application layer

### Access Control
- Principle of least privilege
- Separate read/write users
- Audit all schema changes
- Regular permission reviews

## Development Guidelines

### Schema Changes
1. Create migration file
2. Test migration on dev database
3. Create rollback migration
4. Update ORM models
5. Update documentation
6. Review with team
7. Apply to production during maintenance window

### Testing Database Changes
```bash
# Create test database
createdb greenschool_test

# Apply migrations
psql -d greenschool_test -f migrations/*.sql

# Run tests
pytest tests/

# Drop test database
dropdb greenschool_test
```

## Appendix

### Full Schema SQL
Complete schema SQL files will be created in:
- `docs/schema/complete_schema.sql` - All table definitions
- `docs/schema/indexes.sql` - All index definitions
- `docs/schema/constraints.sql` - All constraint definitions
- `docs/schema/rls_policies.sql` - All RLS policies

### ER Diagram Tool
Generate visual ER diagram using:
```bash
# Using pg_dump and graphviz
postgresql_autodoc -d greenschool -t dot
dot -Tpng greenschool.dot -o schema_diagram.png
```

---

**Next Steps**:
1. Review this schema overview
2. Begin implementing Feature 01 (Users) database schema
3. Create detailed schema documentation per feature
4. Test multi-tenant isolation thoroughly
5. Verify GDPR compliance for all tables
