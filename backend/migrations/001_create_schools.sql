-- Migration: 001_create_schools.sql
-- Created: 2025-10-13
-- Description: Create schools table (multi-tenant foundation)

BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    phone VARCHAR(20),
    email VARCHAR(255),
    website_url VARCHAR(500),
    facebook_url VARCHAR(500),
    twitter_url VARCHAR(500),
    instagram_url VARCHAR(500),
    logo_url VARCHAR(500),
    principal_id UUID,
    hod_id UUID,
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    locale VARCHAR(10) DEFAULT 'en_US',
    settings JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    deleted_at TIMESTAMP,
    deleted_by UUID
);

CREATE INDEX idx_schools_slug ON schools(slug);
CREATE INDEX idx_schools_status ON schools(status);
CREATE INDEX idx_schools_deleted_at ON schools(deleted_at);

COMMENT ON TABLE schools IS 'Multi-tenant foundation - one record per school';
COMMENT ON COLUMN schools.slug IS 'URL-friendly identifier for the school';
COMMENT ON COLUMN schools.principal_id IS 'FK to users table (administrator persona)';
COMMENT ON COLUMN schools.hod_id IS 'FK to users table (head of department)';

-- Insert test school
INSERT INTO schools (name, slug, email, phone, city, state, postal_code)
VALUES (
    'Green Valley Elementary',
    'green-valley',
    'admin@greenschool.edu',
    '+1-555-0100',
    'Springfield',
    'CA',
    '90210'
) ON CONFLICT (slug) DO NOTHING;

COMMIT;
