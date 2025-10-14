# Feature Plan: Schools
**Feature ID**: 02
**Priority**: CRITICAL - Foundation Feature
**Status**: Not Started
**Estimated Time**: 28-36 hours

## Overview
School management system providing multi-tenant foundation with complete school profile management, contact information, and branding.

## Business Requirements (PRD Alignment)

### Core Functionality
- School profile management
- Address and contact information
- Principal and Head of Department assignment
- Social media and website links
- Logo storage in S3 or file system
- School settings and configurations
- Multi-tenant isolation foundation

### Key Business Rules
- Each school is a separate tenant with isolated data
- School name must be unique in system
- Logo images stored securely
- Principal must be a user with administrator persona
- HOD must be a user with teacher persona
- Soft delete required for audit trail

## Database Design

### Table: `schools`
```sql
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL, -- URL-friendly identifier
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
    principal_id UUID REFERENCES users(id),
    hod_id UUID REFERENCES users(id),
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    locale VARCHAR(10) DEFAULT 'en_US',
    settings JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id)
);

CREATE INDEX idx_schools_slug ON schools(slug);
CREATE INDEX idx_schools_status ON schools(status);
CREATE INDEX idx_schools_principal_id ON schools(principal_id);
```

### Sample Data
1. Green Valley Elementary
2. Riverside Primary School
3. Oakwood Academy
4. Sunshine Elementary
5. Meadowbrook School

## API Design

### Base Path: `/api/v1/schools`

### Endpoints
- **POST** `/api/v1/schools` - Create school (System Admin only)
- **GET** `/api/v1/schools` - List schools (System Admin only)
- **GET** `/api/v1/schools/{id}` - Get school details (Admin)
- **PUT** `/api/v1/schools/{id}` - Update school (Admin)
- **DELETE** `/api/v1/schools/{id}` - Delete school (System Admin only)
- **POST** `/api/v1/schools/{id}/upload-logo` - Upload logo
- **GET** `/api/v1/schools/{id}/settings` - Get school settings
- **PUT** `/api/v1/schools/{id}/settings` - Update settings

## UX Design

### Views
1. **Schools List** (`/schools`) - Admin only, table with search/filter
2. **School Detail** (`/schools/{id}`) - Profile view with tabs
3. **School Form** (`/schools/new`, `/schools/{id}/edit`) - Create/edit form
4. **Settings Tab** - School-specific configurations

### Components
- SchoolList.vue
- SchoolDetail.vue
- SchoolForm.vue
- SchoolLogoUpload.vue
- SchoolSettingsForm.vue

## Testing Requirements
- All CRUD operations
- Logo upload/delete
- Principal/HOD assignment validation
- Multi-tenant data isolation
- Settings management
- Soft delete functionality

## Dependencies
- **Requires**: Users feature (for principal_id, hod_id)
- **Required By**: All other features (for school_id)

## GDPR/POPPI Compliance
- Audit logging for all school CRUD
- Soft delete maintains history
- Data export capability

## Implementation Checklist
- [ ] Database schema and migration
- [ ] ORM models
- [ ] Repository layer
- [ ] Service layer
- [ ] API endpoints (5 CRUD + 3 additional)
- [ ] Backend tests (>80% coverage)
- [ ] Pinia store
- [ ] API service
- [ ] Vue components (4)
- [ ] Routing
- [ ] E2E tests
- [ ] Docker testing
- [ ] Documentation

## Acceptance Criteria
- [ ] Full CRUD operations work
- [ ] Logo upload works with S3/file system
- [ ] Principal/HOD assignment works
- [ ] Settings stored and retrieved correctly
- [ ] All tests pass
- [ ] Responsive UI
- [ ] Documentation complete
