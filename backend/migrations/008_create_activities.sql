-- Migration: 008_create_activities.sql
-- Description: Create activities and activity_enrollments tables for extracurricular activities management
-- Date: 2025-10-26

-- Drop tables if exist (for development)
DROP TABLE IF EXISTS activity_enrollments CASCADE;
DROP TABLE IF EXISTS activities CASCADE;

-- Create activities table
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    coordinator_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Identification
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),

    -- Classification
    activity_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),

    -- Description
    description TEXT,

    -- Eligibility
    grade_levels INTEGER[] NOT NULL,
    max_participants INTEGER,
    min_participants INTEGER,

    -- Scheduling
    schedule JSONB DEFAULT '{}',
    start_date DATE,
    end_date DATE,

    -- Location & Logistics
    location VARCHAR(255),
    room_id UUID REFERENCES rooms(id) ON DELETE SET NULL,

    -- Financial
    cost DECIMAL(10,2) DEFAULT 0.00,
    registration_fee DECIMAL(10,2) DEFAULT 0.00,
    equipment_fee DECIMAL(10,2) DEFAULT 0.00,

    -- Requirements
    requirements TEXT[],
    equipment_needed TEXT[],
    uniform_required BOOLEAN DEFAULT FALSE,

    -- Contact & Communication
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    parent_info TEXT,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    is_featured BOOLEAN DEFAULT FALSE,
    registration_open BOOLEAN DEFAULT TRUE,

    -- Display
    photo_url VARCHAR(500),
    color VARCHAR(7),

    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Constraints
    CHECK (status IN ('active', 'full', 'cancelled', 'completed')),
    CHECK (activity_type IN ('sports', 'club', 'art', 'music', 'academic', 'other')),
    CHECK (cost >= 0),
    CHECK (registration_fee >= 0),
    CHECK (equipment_fee >= 0),
    CHECK (max_participants IS NULL OR max_participants > 0),
    CHECK (min_participants IS NULL OR min_participants > 0),
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date),
    UNIQUE(school_id, code)
);

-- Create activity_enrollments table
CREATE TABLE activity_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,

    -- Enrollment Details
    enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- Payment
    payment_status VARCHAR(20) DEFAULT 'pending',
    amount_paid DECIMAL(10,2) DEFAULT 0.00,
    payment_date DATE,

    -- Attendance
    attendance_count INTEGER DEFAULT 0,
    total_sessions INTEGER,

    -- Performance
    performance_notes TEXT,
    achievements TEXT[],

    -- Consent & Requirements
    parent_consent BOOLEAN DEFAULT FALSE,
    parent_consent_date DATE,
    medical_clearance BOOLEAN DEFAULT FALSE,
    emergency_contact_provided BOOLEAN DEFAULT FALSE,

    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    withdrawn_at TIMESTAMP,
    withdrawn_by UUID REFERENCES users(id) ON DELETE SET NULL,
    withdrawn_reason TEXT,

    -- Constraints
    CHECK (status IN ('active', 'waitlisted', 'withdrawn', 'completed')),
    CHECK (payment_status IN ('pending', 'partial', 'paid', 'waived')),
    CHECK (amount_paid >= 0),
    CHECK (attendance_count >= 0),
    UNIQUE(activity_id, student_id)
);

-- Create indexes for activities
CREATE INDEX idx_activities_school_id ON activities(school_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_coordinator_id ON activities(coordinator_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_activity_type ON activities(activity_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_status ON activities(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_grade_levels ON activities USING GIN(grade_levels) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_deleted_at ON activities(deleted_at);
CREATE INDEX idx_activities_code ON activities(school_id, code) WHERE deleted_at IS NULL;
CREATE INDEX idx_activities_featured ON activities(school_id, is_featured) WHERE deleted_at IS NULL AND is_featured = TRUE;

-- Create indexes for activity_enrollments
CREATE INDEX idx_enrollments_activity_id ON activity_enrollments(activity_id);
CREATE INDEX idx_enrollments_student_id ON activity_enrollments(student_id);
CREATE INDEX idx_enrollments_status ON activity_enrollments(status);
CREATE INDEX idx_enrollments_payment_status ON activity_enrollments(payment_status);
CREATE INDEX idx_enrollments_enrollment_date ON activity_enrollments(enrollment_date);

-- Add RLS (Row Level Security) for multi-tenancy
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_enrollments ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see activities from their school
CREATE POLICY activities_school_isolation ON activities
    USING (school_id = current_setting('app.current_school_id', TRUE)::UUID);

-- Policy: Users can only see enrollments for activities in their school
CREATE POLICY enrollments_school_isolation ON activity_enrollments
    USING (
        activity_id IN (
            SELECT id FROM activities WHERE school_id = current_setting('app.current_school_id', TRUE)::UUID
        )
    );

-- Add comments on activities table
COMMENT ON TABLE activities IS 'Extracurricular activities including sports, clubs, art, music, and academic programs';
COMMENT ON COLUMN activities.activity_type IS 'Type of activity: sports, club, art, music, academic, other';
COMMENT ON COLUMN activities.grade_levels IS 'Array of eligible grade levels (1-7)';
COMMENT ON COLUMN activities.schedule IS 'JSONB containing days of week, start_time, end_time';
COMMENT ON COLUMN activities.requirements IS 'Array of requirements (e.g., "Parent consent", "Medical clearance")';
COMMENT ON COLUMN activities.equipment_needed IS 'Array of equipment students need to bring/purchase';
COMMENT ON COLUMN activities.status IS 'Activity status: active, full, cancelled, completed';
COMMENT ON COLUMN activities.registration_open IS 'Whether new students can register';

-- Add comments on activity_enrollments table
COMMENT ON TABLE activity_enrollments IS 'Student enrollments in extracurricular activities';
COMMENT ON COLUMN activity_enrollments.status IS 'Enrollment status: active, waitlisted, withdrawn, completed';
COMMENT ON COLUMN activity_enrollments.payment_status IS 'Payment status: pending, partial, paid, waived';
COMMENT ON COLUMN activity_enrollments.parent_consent IS 'Whether parent/guardian has provided consent';
COMMENT ON COLUMN activity_enrollments.medical_clearance IS 'Whether student has medical clearance (if required)';
