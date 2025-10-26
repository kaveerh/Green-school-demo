-- Migration: 007_create_events.sql
-- Description: Create events table for school calendar management
-- Date: 2025-10-25

-- Drop table if exists (for development)
DROP TABLE IF EXISTS events CASCADE;

-- Create events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,

    -- Event details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,

    -- Scheduling
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    is_all_day BOOLEAN DEFAULT FALSE,

    -- Location
    location VARCHAR(255),
    room_id UUID REFERENCES rooms(id) ON DELETE SET NULL,

    -- Participants
    target_audience VARCHAR(50), -- all_school, grade_level, class, custom
    grade_levels INTEGER[], -- Array of grade levels (1-7)
    class_ids UUID[], -- Array of class IDs

    -- Organization
    organizer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    organizer_name VARCHAR(255),

    -- Settings
    status VARCHAR(20) DEFAULT 'scheduled',
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(50), -- daily, weekly, monthly, yearly
    recurrence_end_date DATE,

    -- Attendance tracking
    requires_rsvp BOOLEAN DEFAULT FALSE,
    max_attendees INTEGER,
    current_attendees INTEGER DEFAULT 0,

    -- Additional info
    color VARCHAR(7), -- Hex color for calendar display
    reminder_sent BOOLEAN DEFAULT FALSE,
    attachments JSONB, -- Array of attachment URLs/metadata

    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Constraints
    CHECK (end_date >= start_date),
    CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'postponed')),
    CHECK (event_type IN ('assembly', 'exam', 'holiday', 'meeting', 'parent_conference', 'field_trip', 'sports', 'performance', 'workshop', 'other')),
    CHECK (target_audience IN ('all_school', 'grade_level', 'class', 'custom')),
    CHECK (recurrence_pattern IS NULL OR recurrence_pattern IN ('daily', 'weekly', 'monthly', 'yearly'))
);

-- Create indexes for performance
CREATE INDEX idx_events_school_id ON events(school_id);
CREATE INDEX idx_events_start_date ON events(start_date);
CREATE INDEX idx_events_end_date ON events(end_date);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_target_audience ON events(target_audience);
CREATE INDEX idx_events_organizer_id ON events(organizer_id);
CREATE INDEX idx_events_room_id ON events(room_id);
CREATE INDEX idx_events_deleted_at ON events(deleted_at);
CREATE INDEX idx_events_date_range ON events(school_id, start_date, end_date);

-- Add RLS (Row Level Security) for multi-tenancy
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see events from their school
CREATE POLICY events_school_isolation ON events
    USING (school_id = current_setting('app.current_school_id', TRUE)::UUID);

-- Add comments on table
COMMENT ON TABLE events IS 'School calendar events including assemblies, exams, holidays, meetings, and more';
COMMENT ON COLUMN events.event_type IS 'Type of event: assembly, exam, holiday, meeting, parent_conference, field_trip, sports, performance, workshop, other';
COMMENT ON COLUMN events.target_audience IS 'Who the event is for: all_school, grade_level, class, custom';
COMMENT ON COLUMN events.grade_levels IS 'Array of grade levels (1-7) if target_audience is grade_level';
COMMENT ON COLUMN events.class_ids IS 'Array of class IDs if target_audience is class';
COMMENT ON COLUMN events.is_recurring IS 'Whether this event repeats';
COMMENT ON COLUMN events.recurrence_pattern IS 'How often the event repeats: daily, weekly, monthly, yearly';
COMMENT ON COLUMN events.color IS 'Hex color code for calendar display (e.g., #FF5733)';
