-- Migration: Create Merits Table
-- Feature: Merits (Merit/Reward System)
-- Description: Positive behavior reinforcement and achievement recognition system

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
    batch_id UUID,  -- Groups merits awarded together (for class awards)

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

-- Indexes for performance
CREATE INDEX idx_merits_school_id ON merits(school_id);
CREATE INDEX idx_merits_student_id ON merits(student_id);
CREATE INDEX idx_merits_awarded_by_id ON merits(awarded_by_id);
CREATE INDEX idx_merits_class_id ON merits(class_id);
CREATE INDEX idx_merits_category ON merits(category);
CREATE INDEX idx_merits_awarded_date ON merits(awarded_date);
CREATE INDEX idx_merits_quarter ON merits(quarter);
CREATE INDEX idx_merits_deleted_at ON merits(deleted_at);
CREATE INDEX idx_merits_batch_id ON merits(batch_id) WHERE batch_id IS NOT NULL;

-- Composite index for common queries
CREATE INDEX idx_merits_student_quarter ON merits(student_id, quarter) WHERE deleted_at IS NULL;
CREATE INDEX idx_merits_school_date ON merits(school_id, awarded_date) WHERE deleted_at IS NULL;

-- Row Level Security
ALTER TABLE merits ENABLE ROW LEVEL SECURITY;

CREATE POLICY merits_school_isolation ON merits
    USING (school_id = current_setting('app.current_school_id')::UUID);

-- Comments
COMMENT ON TABLE merits IS 'Merit points awarded to students for achievements and positive behavior';
COMMENT ON COLUMN merits.category IS 'Type of merit: academic, behavior, participation, leadership, attendance, other';
COMMENT ON COLUMN merits.points IS 'Merit points awarded (1-10 scale)';
COMMENT ON COLUMN merits.batch_id IS 'Groups merits awarded together, used for class-wide awards';
COMMENT ON COLUMN merits.is_class_award IS 'Indicates if this was part of a class-wide merit award';
