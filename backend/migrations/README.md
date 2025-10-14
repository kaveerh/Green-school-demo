# Database Migrations

## Overview
This directory contains SQL migration files for the Green School Management System database.

## Migration Files
- `001_create_schools.sql` - Creates schools table (multi-tenant foundation)
- `002_create_users.sql` - Creates users table with RLS policies

## Running Migrations

### Option 1: Using Docker (Recommended)
```bash
# Start PostgreSQL container
cd /Users/kaveerh/claude-projects
docker-compose up -d database

# Wait for database to be ready
docker-compose logs database

# Run migrations in order
docker exec -i greenschool-db psql -U postgres -d greenschool < backend/migrations/001_create_schools.sql
docker exec -i greenschool-db psql -U postgres -d greenschool < backend/migrations/002_create_users.sql
```

### Option 2: Using psql directly
```bash
# Ensure PostgreSQL is running on localhost:5432
psql -U postgres -d greenschool -f backend/migrations/001_create_schools.sql
psql -U postgres -d greenschool -f backend/migrations/002_create_users.sql
```

### Option 3: Auto-load on container start
The docker-compose.yml is configured to automatically run migration files from this directory when the database container first starts.

## Verifying Migrations

```bash
# Connect to database
docker exec -it greenschool-db psql -U postgres -d greenschool

# List tables
\dt

# Describe schools table
\d+ schools

# Describe users table
\d+ users

# View sample data
SELECT * FROM schools;
SELECT id, email, first_name, last_name, persona FROM users;

# Exit
\q
```

## Test Data Created

### Schools
- Green Valley Elementary (slug: green-valley)

### Users (all linked to Green Valley)
1. **Administrator**: admin@greenschool.edu
2. **Teacher**: john.smith@greenschool.edu
3. **Student**: alice.student@greenschool.edu
4. **Parent**: mary.parent@greenschool.edu
5. **Vendor**: supplies@vendor.com

## Row Level Security (RLS)

The users table has RLS enabled with two policies:
1. **users_school_isolation**: Ensures users can only access data from their school
2. **users_view_self**: Allows users to view their own data

### Setting Session Variables for RLS
```sql
-- Set current school context
SET app.current_school_id = '<school-uuid>';

-- Set current user context
SET app.current_user_id = '<user-uuid>';

-- Set user role
SET app.user_role = 'system_admin'; -- or 'teacher', 'student', etc.
```

## Adding New Migrations

1. Create a new file: `003_description.sql`
2. Follow the template:
```sql
-- Migration: 003_description.sql
-- Created: YYYY-MM-DD
-- Description: What this migration does

BEGIN;

-- Your SQL here

COMMIT;
```
3. Document the migration in this README
4. Run the migration using one of the methods above

## Rollback (if needed)

To rollback migrations, you'll need to manually reverse the changes:
```bash
# Drop tables in reverse order
docker exec -it greenschool-db psql -U postgres -d greenschool -c "DROP TABLE IF EXISTS users CASCADE;"
docker exec -it greenschool-db psql -U postgres -d greenschool -c "DROP TABLE IF EXISTS schools CASCADE;"
```

## Next Migrations

Follow the feature development order from docs/MASTER_FEATURE_PLAN.md:
- 003: Teachers table
- 004: Students table
- 005: Parents table and parent_student_relationships
- 006: Subjects table
- And so on...
