-- =====================================================
-- Migration: 005 - Create Assessments Table
-- Description: Assessments for students with grades, scores, and evaluation
-- Date: 2025-10-24
-- =====================================================

-- Create assessments table
CREATE TABLE IF NOT EXISTS assessments (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Keys
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,

    -- Assessment Details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    assessment_type VARCHAR(50) NOT NULL, -- test, quiz, project, assignment, exam, presentation
    quarter VARCHAR(2) NOT NULL, -- Q1, Q2, Q3, Q4
    assessment_date DATE NOT NULL,
    due_date DATE,

    -- Grading
    total_points DECIMAL(10, 2) NOT NULL,
    points_earned DECIMAL(10, 2),
    percentage DECIMAL(5, 2), -- Computed as (points_earned / total_points) * 100
    letter_grade VARCHAR(2), -- A+, A, A-, B+, B, B-, C+, C, C-, D, F

    -- Status and Feedback
    status VARCHAR(20) DEFAULT 'pending', -- pending, graded, returned, late
    feedback TEXT,
    graded_at TIMESTAMP WITH TIME ZONE,
    returned_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    weight DECIMAL(5, 2) DEFAULT 1.0, -- Weight of assessment in final grade
    is_extra_credit BOOLEAN DEFAULT FALSE,
    is_makeup BOOLEAN DEFAULT FALSE,

    -- Base model fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,

    -- Constraints
    CONSTRAINT chk_assessments_quarter CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    CONSTRAINT chk_assessments_type CHECK (
        assessment_type IN ('test', 'quiz', 'project', 'assignment', 'exam', 'presentation', 'homework', 'lab', 'other')
    ),
    CONSTRAINT chk_assessments_status CHECK (
        status IN ('pending', 'submitted', 'graded', 'returned', 'late', 'missing', 'excused')
    ),
    CONSTRAINT chk_assessments_letter_grade CHECK (
        letter_grade IS NULL OR letter_grade IN (
            'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F'
        )
    ),
    CONSTRAINT chk_assessments_total_points CHECK (total_points > 0),
    CONSTRAINT chk_assessments_points_earned CHECK (points_earned IS NULL OR points_earned >= 0),
    CONSTRAINT chk_assessments_percentage CHECK (percentage IS NULL OR (percentage >= 0 AND percentage <= 100)),
    CONSTRAINT chk_assessments_weight CHECK (weight >= 0 AND weight <= 10)
);

-- Create indexes for better query performance
CREATE INDEX idx_assessments_school_id ON assessments(school_id);
CREATE INDEX idx_assessments_student_id ON assessments(student_id);
CREATE INDEX idx_assessments_class_id ON assessments(class_id);
CREATE INDEX idx_assessments_subject_id ON assessments(subject_id);
CREATE INDEX idx_assessments_teacher_id ON assessments(teacher_id);
CREATE INDEX idx_assessments_quarter ON assessments(quarter);
CREATE INDEX idx_assessments_type ON assessments(assessment_type);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_assessments_assessment_date ON assessments(assessment_date);
CREATE INDEX idx_assessments_deleted_at ON assessments(deleted_at);
CREATE INDEX idx_assessments_student_quarter ON assessments(student_id, quarter);
CREATE INDEX idx_assessments_class_quarter ON assessments(class_id, quarter);

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_assessments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_assessments_updated_at
    BEFORE UPDATE ON assessments
    FOR EACH ROW
    EXECUTE FUNCTION update_assessments_updated_at();

-- Insert sample assessments data
INSERT INTO assessments (
    school_id, student_id, class_id, subject_id, teacher_id,
    title, description, assessment_type, quarter, assessment_date, due_date,
    total_points, points_earned, percentage, letter_grade,
    status, feedback, graded_at, weight
) VALUES
-- Sample Assessment 1: Math Quiz Q1
(
    (SELECT id FROM schools LIMIT 1),
    (SELECT id FROM students LIMIT 1),
    (SELECT id FROM classes LIMIT 1),
    (SELECT id FROM subjects WHERE name LIKE '%Math%' LIMIT 1),
    (SELECT id FROM teachers LIMIT 1),
    'Fractions Quiz',
    'Quiz covering addition and subtraction of fractions',
    'quiz',
    'Q1',
    '2025-09-15',
    '2025-09-15',
    20.0,
    18.0,
    90.0,
    'A-',
    'graded',
    'Excellent work! Just watch the negative signs.',
    '2025-09-16 14:30:00',
    1.0
),
-- Sample Assessment 2: Science Project Q1
(
    (SELECT id FROM schools LIMIT 1),
    (SELECT id FROM students LIMIT 1),
    (SELECT id FROM classes LIMIT 1),
    (SELECT id FROM subjects WHERE name LIKE '%Science%' LIMIT 1),
    (SELECT id FROM teachers LIMIT 1),
    'Solar System Model',
    'Create a 3D model of the solar system',
    'project',
    'Q1',
    '2025-09-25',
    '2025-09-25',
    50.0,
    45.0,
    90.0,
    'A-',
    'returned',
    'Creative and accurate model. Great attention to detail!',
    '2025-09-27 10:00:00',
    2.0
),
-- Sample Assessment 3: English Essay Q2
(
    (SELECT id FROM schools LIMIT 1),
    (SELECT id FROM students LIMIT 1),
    (SELECT id FROM classes LIMIT 1),
    (SELECT id FROM subjects WHERE name LIKE '%English%' LIMIT 1),
    (SELECT id FROM teachers LIMIT 1),
    'Book Report: Charlotte''s Web',
    'Write a 3-paragraph book report',
    'assignment',
    'Q2',
    '2025-11-10',
    '2025-11-10',
    30.0,
    27.0,
    90.0,
    'A-',
    'graded',
    'Well-written report with good analysis of themes.',
    '2025-11-12 16:00:00',
    1.5
),
-- Sample Assessment 4: Math Test Q2 (pending)
(
    (SELECT id FROM schools LIMIT 1),
    (SELECT id FROM students LIMIT 1),
    (SELECT id FROM classes LIMIT 1),
    (SELECT id FROM subjects WHERE name LIKE '%Math%' LIMIT 1),
    (SELECT id FROM teachers LIMIT 1),
    'Multiplication and Division Test',
    'Comprehensive test on multiplication and division',
    'test',
    'Q2',
    '2025-11-20',
    '2025-11-20',
    100.0,
    NULL,
    NULL,
    NULL,
    'pending',
    NULL,
    NULL,
    3.0
),
-- Sample Assessment 5: Science Lab Q2
(
    (SELECT id FROM schools LIMIT 1),
    (SELECT id FROM students LIMIT 1),
    (SELECT id FROM classes LIMIT 1),
    (SELECT id FROM subjects WHERE name LIKE '%Science%' LIMIT 1),
    (SELECT id FROM teachers LIMIT 1),
    'Plant Growth Experiment',
    'Weekly observations of plant growth under different conditions',
    'lab',
    'Q2',
    '2025-10-30',
    '2025-10-30',
    40.0,
    38.0,
    95.0,
    'A',
    'graded',
    'Excellent data collection and analysis!',
    '2025-11-01 15:00:00',
    2.0
);

-- Add comment to table
COMMENT ON TABLE assessments IS 'Student assessments with grades, scores, and teacher feedback';
COMMENT ON COLUMN assessments.quarter IS 'Academic quarter: Q1, Q2, Q3, or Q4';
COMMENT ON COLUMN assessments.assessment_type IS 'Type of assessment: test, quiz, project, assignment, etc.';
COMMENT ON COLUMN assessments.status IS 'Current status: pending, submitted, graded, returned, late, missing, excused';
COMMENT ON COLUMN assessments.letter_grade IS 'Letter grade: A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F';
COMMENT ON COLUMN assessments.weight IS 'Weight of assessment in final grade calculation';
COMMENT ON COLUMN assessments.is_extra_credit IS 'Whether this assessment is for extra credit';
COMMENT ON COLUMN assessments.is_makeup IS 'Whether this is a makeup assessment';
