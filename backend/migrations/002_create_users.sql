-- Migration: 002_create_users.sql
-- Created: 2025-10-13
-- Description: Create users table (authentication foundation)

BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    persona VARCHAR(50) NOT NULL CHECK (persona IN ('administrator', 'teacher', 'student', 'parent', 'vendor')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    keycloak_id VARCHAR(255) UNIQUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id)
);

CREATE INDEX idx_users_school_id ON users(school_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_persona ON users(persona);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_keycloak_id ON users(keycloak_id);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);

COMMENT ON TABLE users IS 'All system users across 5 personas';
COMMENT ON COLUMN users.persona IS 'User role: administrator, teacher, student, parent, vendor';
COMMENT ON COLUMN users.keycloak_id IS 'Keycloak user ID for SSO integration';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt password hash (optional if using Keycloak only)';

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for school isolation
-- Note: This policy uses session variables that must be set by the application
CREATE POLICY users_school_isolation ON users
    USING (
        school_id::text = current_setting('app.current_school_id', true)
        OR current_setting('app.user_role', true) = 'system_admin'
    );

-- Create RLS policy for users to view their own data
CREATE POLICY users_view_self ON users
    FOR SELECT
    USING (
        id::text = current_setting('app.current_user_id', true)
        OR school_id::text = current_setting('app.current_school_id', true)
    );

-- Insert test admin user linked to test school
DO $$
DECLARE
    v_school_id UUID;
BEGIN
    -- Get the test school ID
    SELECT id INTO v_school_id FROM schools WHERE slug = 'green-valley';

    -- Insert admin user
    INSERT INTO users (
        school_id,
        email,
        first_name,
        last_name,
        persona,
        status,
        email_verified,
        metadata
    )
    VALUES (
        v_school_id,
        'admin@greenschool.edu',
        'Admin',
        'User',
        'administrator',
        'active',
        true,
        '{"role": "system_admin", "department": "Administration"}'::jsonb
    ) ON CONFLICT (email) DO NOTHING;

    -- Insert test teacher
    INSERT INTO users (
        school_id,
        email,
        first_name,
        last_name,
        persona,
        status,
        email_verified
    )
    VALUES (
        v_school_id,
        'john.smith@greenschool.edu',
        'John',
        'Smith',
        'teacher',
        'active',
        true
    ) ON CONFLICT (email) DO NOTHING;

    -- Insert test student
    INSERT INTO users (
        school_id,
        email,
        first_name,
        last_name,
        persona,
        status,
        email_verified
    )
    VALUES (
        v_school_id,
        'alice.student@greenschool.edu',
        'Alice',
        'Johnson',
        'student',
        'active',
        true
    ) ON CONFLICT (email) DO NOTHING;

    -- Insert test parent
    INSERT INTO users (
        school_id,
        email,
        first_name,
        last_name,
        persona,
        status,
        email_verified
    )
    VALUES (
        v_school_id,
        'mary.parent@greenschool.edu',
        'Mary',
        'Johnson',
        'parent',
        'active',
        true
    ) ON CONFLICT (email) DO NOTHING;

    -- Insert test vendor
    INSERT INTO users (
        school_id,
        email,
        first_name,
        last_name,
        persona,
        status,
        email_verified
    )
    VALUES (
        v_school_id,
        'supplies@vendor.com',
        'Supply',
        'Vendor',
        'vendor',
        'active',
        true
    ) ON CONFLICT (email) DO NOTHING;
END $$;

COMMIT;
