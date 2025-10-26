-- Migration: 006_create_attendance.sql
-- Description: Create attendance table for daily student attendance tracking
-- Date: 2025-10-24

-- Drop table if exists (for development)
DROP TABLE IF EXISTS attendance CASCADE;

-- Create attendance table
CREATE TABLE attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE SET NULL,

    -- Attendance details
    attendance_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'tardy', 'excused', 'sick')),

    -- Time tracking
    check_in_time TIME,
    check_out_time TIME,

    -- Additional information
    notes TEXT,
    recorded_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Parent notification
    parent_notified BOOLEAN DEFAULT FALSE,
    notified_at TIMESTAMP,

    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Unique constraint: one attendance record per student per class per date
    UNIQUE(student_id, class_id, attendance_date),

    -- For homeroom attendance (no class assigned)
    CHECK (class_id IS NULL OR class_id IS NOT NULL)
);

-- Create indexes for performance
CREATE INDEX idx_attendance_school_id ON attendance(school_id);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_class_id ON attendance(class_id);
CREATE INDEX idx_attendance_date ON attendance(attendance_date);
CREATE INDEX idx_attendance_status ON attendance(status);
CREATE INDEX idx_attendance_student_date ON attendance(student_id, attendance_date);
CREATE INDEX idx_attendance_class_date ON attendance(class_id, attendance_date);
CREATE INDEX idx_attendance_school_date ON attendance(school_id, attendance_date);
CREATE INDEX idx_attendance_deleted_at ON attendance(deleted_at);

-- Add RLS (Row Level Security) for multi-tenancy
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see attendance from their school
CREATE POLICY attendance_school_isolation ON attendance
    USING (school_id = current_setting('app.current_school_id', TRUE)::UUID);

-- Add comment on table
COMMENT ON TABLE attendance IS 'Daily student attendance tracking with status, check-in/out times, and parent notification';
COMMENT ON COLUMN attendance.status IS 'Attendance status: present, absent, tardy, excused, sick';
COMMENT ON COLUMN attendance.class_id IS 'NULL for homeroom attendance, otherwise specific class';
COMMENT ON COLUMN attendance.parent_notified IS 'Whether parent has been notified of absence/tardiness';
