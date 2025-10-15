-- Migration: 003_create_teachers_table.sql
-- Created: 2025-10-15
-- Description: Create teachers table for teacher profiles and assignments

BEGIN;

-- Create teachers table
CREATE TABLE IF NOT EXISTS teachers (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Foreign keys
  school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- Teacher-specific fields
  employee_id VARCHAR(50) NOT NULL,
  hire_date DATE NOT NULL,
  termination_date DATE,
  department VARCHAR(100),
  job_title VARCHAR(100) DEFAULT 'Teacher',

  -- Teaching credentials
  certification_number VARCHAR(100),
  certification_expiry DATE,
  education_level VARCHAR(50), -- Bachelor's, Master's, PhD
  university VARCHAR(200),

  -- Teaching assignments
  grade_levels INT[] NOT NULL DEFAULT '{}', -- Array of grades 1-7
  specializations TEXT[] DEFAULT '{}', -- Array of subject specializations

  -- Employment details
  employment_type VARCHAR(20) DEFAULT 'full-time', -- full-time, part-time, contract, substitute
  salary DECIMAL(10, 2),
  work_hours_per_week INT DEFAULT 40,

  -- Contact and emergency
  emergency_contact_name VARCHAR(200),
  emergency_contact_phone VARCHAR(20),
  emergency_contact_relationship VARCHAR(50),

  -- Status
  status VARCHAR(20) DEFAULT 'active', -- active, inactive, on_leave, terminated
  is_active BOOLEAN DEFAULT true,

  -- Metadata and settings
  bio TEXT,
  office_room VARCHAR(50),
  office_hours JSONB DEFAULT '{}',
  preferences JSONB DEFAULT '{}',

  -- Audit trail
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  updated_by UUID REFERENCES users(id),
  deleted_at TIMESTAMP,
  deleted_by UUID REFERENCES users(id),

  -- Constraints
  CONSTRAINT teachers_user_id_key UNIQUE (user_id),
  CONSTRAINT chk_teachers_status CHECK (
    status IN ('active', 'inactive', 'on_leave', 'terminated')
  ),
  CONSTRAINT chk_teachers_employment_type CHECK (
    employment_type IN ('full-time', 'part-time', 'contract', 'substitute')
  ),
  CONSTRAINT chk_teachers_grade_levels CHECK (
    grade_levels <@ ARRAY[1,2,3,4,5,6,7]::INT[]
  ),
  CONSTRAINT chk_teachers_education_level CHECK (
    education_level IS NULL OR
    education_level IN ('High School', 'Associate', 'Bachelor''s', 'Master''s', 'PhD', 'Other')
  ),
  CONSTRAINT chk_teachers_salary CHECK (salary IS NULL OR salary >= 0),
  CONSTRAINT chk_teachers_work_hours CHECK (work_hours_per_week IS NULL OR work_hours_per_week > 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_teachers_school_id ON teachers(school_id);
CREATE INDEX IF NOT EXISTS idx_teachers_user_id ON teachers(user_id);
CREATE INDEX IF NOT EXISTS idx_teachers_employee_id ON teachers(school_id, employee_id);
CREATE INDEX IF NOT EXISTS idx_teachers_status ON teachers(status);
CREATE INDEX IF NOT EXISTS idx_teachers_employment_type ON teachers(employment_type);
CREATE INDEX IF NOT EXISTS idx_teachers_deleted_at ON teachers(deleted_at);
CREATE INDEX IF NOT EXISTS idx_teachers_grade_levels ON teachers USING GIN (grade_levels);
CREATE INDEX IF NOT EXISTS idx_teachers_specializations ON teachers USING GIN (specializations);

-- Enable Row Level Security
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;

-- RLS Policy: School isolation
CREATE POLICY teachers_school_isolation ON teachers
  USING (
    school_id::text = current_setting('app.current_school_id', true) OR
    current_setting('app.user_role', true) = 'system_admin'
  );

-- RLS Policy: Teachers can view their own profile
CREATE POLICY teachers_view_self ON teachers
  FOR SELECT
  USING (
    user_id::text = current_setting('app.current_user_id', true) OR
    school_id::text = current_setting('app.current_school_id', true)
  );

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_teachers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_teachers_updated_at
  BEFORE UPDATE ON teachers
  FOR EACH ROW
  EXECUTE FUNCTION update_teachers_updated_at();

COMMIT;

-- Rollback instructions (save in 003_rollback.sql):
-- DROP TRIGGER IF EXISTS trigger_teachers_updated_at ON teachers;
-- DROP FUNCTION IF EXISTS update_teachers_updated_at();
-- DROP POLICY IF EXISTS teachers_view_self ON teachers;
-- DROP POLICY IF EXISTS teachers_school_isolation ON teachers;
-- DROP TABLE IF EXISTS teachers CASCADE;
