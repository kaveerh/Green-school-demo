# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Green School Management System - A comprehensive digital platform for primary school administration (Grades 1-7), featuring student management, assessment tracking, lesson planning, and progress monitoring with GDPR/POPPI compliance.

**Tech Stack:**
- Frontend: Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS
- Backend: Python API + TypeScript + PostgreSQL
- Auth: Keycloak
- Database: PostgreSQL with Row Level Security (multi-tenant)
- Deployment: Docker containers

## Development Commands

### Docker Environment
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up -d --build

# View logs
docker-compose logs -f [service-name]
```

### Frontend (Vue 3 - Port 3000)
```bash
cd frontend
npm install
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
npm run test         # Run Playwright tests
npm run lint         # Lint code
```

### Backend (Python API - Port 8000)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload  # Development server
python -m pytest                      # Run tests
python -m pytest --cov               # Run tests with coverage
```

### Database (PostgreSQL - Port 5432)
```bash
# Connect to database
psql -h localhost -p 5432 -U postgres -d greenschool

# Run migrations
psql -h localhost -p 5432 -U postgres -d greenschool -f migrations/001_initial_schema.sql

# Backup database
pg_dump -h localhost -p 5432 -U postgres greenschool > backup.sql
```

### Testing
```bash
# Backend API tests
cd backend && python -m pytest

# Frontend E2E tests (Playwright)
cd frontend && npm run test

# Docker-based testing
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Architecture

### Multi-Tenant Architecture
- **School-based isolation**: All tables include `school_id` for tenant separation
- **Row Level Security (RLS)**: PostgreSQL RLS policies enforce data isolation
- **UUID primary keys**: All entities use UUIDs for distributed system compatibility

### Authentication Flow
- **Provider**: Keycloak (port 8080)
- **Realm**: Green-School-id
- **Client ID**: Green-School-id
- **Config**: http://localhost:8080/realms/Green-School-id/.well-known/openid-configuration
- **Test Credentials**: admin@greenschool.edu / Password123

### Frontend Architecture (Vue 3)
- **State Management**: Pinia stores per feature domain
- **Routing**: Vue Router 3 with nested routes and auth guards
- **Components**: Composable-based architecture with Headless UI
- **API Layer**: Fetch API with centralized error handling
- **Forms**: Vue Hook Form with schema validation

### Backend Architecture (Python + TypeScript)
- **Pattern**: Repository pattern with ORM (SQLAlchemy)
- **Layers**: Controllers → Services → Repositories → Models
- **Validation**: express-validator for input validation
- **Security**: Helmet, CORS, rate limiting, API key authentication
- **Logging**: Morgan for HTTP requests, audit logging for GDPR

### Database Architecture
- **14 Core Tables**: Schools, Users, Students, Parents, Teachers, Subjects, Rooms, Classes, Events, Assessments, Attendance, Activities, Vendors, Lessons, Merits
- **Relationships**: Many-to-many through junction tables
- **Audit Trail**: Complete CRUD logging for compliance
- **Schema Docs**: See `docs/schema/` for detailed table definitions

## Development Workflow

### Feature Development Checklist (CRITICAL)
When adding any new feature or route, follow this checklist in order:

1. **Planning Phase**
   - [ ] Review feature plan in `docs/features/[feature-name]-plan.md`
   - [ ] Review PRD requirements
   - [ ] Create task checklist

2. **Database Phase**
   - [ ] Design database schema (see `docs/schema/`)
   - [ ] Create migration SQL file
   - [ ] Apply migration
   - [ ] Update ORM models
   - [ ] Create sample data (5 records minimum)
   - [ ] Document schema changes
   - [ ] Commit to git

3. **API Phase**
   - [ ] Create/update repository layer
   - [ ] Create/update service layer
   - [ ] Create/update controller with full CRUD (Create, Read, List, Update, Delete)
   - [ ] Add input validation schemas
   - [ ] Add API route registration
   - [ ] Test all endpoints manually
   - [ ] Update API documentation in `docs/api/`
   - [ ] Commit to git

4. **UX Phase**
   - [ ] Create Pinia store for state management
   - [ ] Create API service methods
   - [ ] Create Vue components (List, Create, Edit, Detail views)
   - [ ] Add routing configuration
   - [ ] Implement form validation
   - [ ] Add loading and error states
   - [ ] Update navigation menus
   - [ ] Update `docs/ux/` documentation
   - [ ] Commit to git

5. **Testing Phase**
   - [ ] Write backend unit tests (pytest)
   - [ ] Write API integration tests
   - [ ] Write Playwright E2E tests for UX flows
   - [ ] Run full test suite in Docker
   - [ ] Verify CRUD operations work end-to-end
   - [ ] Commit to git

6. **Documentation Phase**
   - [ ] Update feature plan with completion status
   - [ ] Update API documentation
   - [ ] Update user documentation
   - [ ] Update CHANGELOG
   - [ ] Commit to git

### Build One Route at a Time
- Complete ALL phases (Database → API → UX → Testing → Documentation) for ONE route before moving to the next
- Ensure full CRUD operations work before proceeding
- Test multi-tenancy isolation for each route
- Verify GDPR compliance (audit logging, consent checks)

## Key Business Rules

### Grade Levels
- System supports ONLY Grades 1-7 (primary school focus)
- All students must be assigned to a valid grade level
- Teachers can be assigned to multiple grade levels

### Academic Organization
- **Quarters**: All planning and assessments organized by Q1, Q2, Q3, Q4
- **Subjects**: Core subjects (MATH, ELA, SCIENCE, SOCIAL_STUDIES, ART, PE)
- **Classes**: Teachers assigned to subjects per grade level

### User Roles & Permissions
- **Administrator**: Full system access, user management, school settings
- **Teacher**: Manage assigned classes, assessments, attendance, lesson plans
- **Student**: View grades, assignments, personal attendance
- **Parent**: Monitor children's progress, view reports, communicate with teachers
- **Vendor**: View event attendance, supply orders, communicate with admin

### GDPR/POPPI Compliance
- Parental consent required for all student data processing
- Complete audit logging of all CRUD operations
- Data retention policies enforced
- Right to deletion must be honored
- Data export capabilities required

### Multi-Tenancy
- Complete data isolation between schools using `school_id`
- RLS policies enforce tenant boundaries
- No cross-tenant queries allowed
- Each school has independent user base

## Code Organization

### Frontend Structure
```
frontend/
├── src/
│   ├── components/     # Reusable Vue components
│   ├── views/          # Page-level components
│   ├── stores/         # Pinia stores (per feature)
│   ├── router/         # Route definitions
│   ├── services/       # API service layer
│   ├── composables/    # Reusable composition functions
│   ├── types/          # TypeScript type definitions
│   └── utils/          # Helper functions
```

### Backend Structure
```
backend/
├── models/            # SQLAlchemy ORM models
├── repositories/      # Data access layer
├── services/          # Business logic layer
├── controllers/       # HTTP request handlers
├── schemas/           # Validation schemas
├── middleware/        # Auth, logging, error handling
├── migrations/        # Database migration files
└── tests/             # pytest test suites
```

### Documentation Structure
```
docs/
├── features/          # Individual feature plans (15 total)
├── schema/            # Database schema documentation
├── api/               # API endpoint documentation
├── ux/                # UX flow documentation
└── plans/             # Project planning documents
```

## Important Patterns

### Separation of Concerns
- **Models**: Database schema definitions only
- **Repositories**: Database queries and data access
- **Services**: Business logic and validation
- **Controllers**: HTTP request/response handling
- **Schemas**: Input/output validation

### Reusability
- Base repository class provides common CRUD operations
- Base model class provides common fields (id, created_at, updated_at, school_id)
- Composable functions for shared frontend logic
- Shared validation schemas across API endpoints

### Extensibility
- Adding new entities follows established patterns
- No changes to existing code required for new features
- Plugin-based middleware architecture
- Component-based UI with composition API

### Testability
- Each layer can be tested independently
- Dependency injection for services
- Mock implementations for testing
- Isolated test databases per test suite

## API Endpoints

All API routes follow RESTful conventions with full CRUD:

```
/api/v1/users           # User management (all personas)
/api/v1/schools         # School management
/api/v1/parents         # Parent management
/api/v1/students        # Student management
/api/v1/teachers        # Teacher management
/api/v1/subjects        # Subject management
/api/v1/rooms           # Room/facility management
/api/v1/events          # Event management
/api/v1/classes         # Class management
/api/v1/assessments     # Assessment management
/api/v1/attendance      # Attendance tracking
/api/v1/activities      # Activity management
/api/v1/vendors         # Vendor management
/api/v1/lessons         # Lesson planning
/api/v1/merits          # Merit/reward system
```

**CRUD Operations** (all endpoints):
- `GET /api/v1/{resource}` - List all (with pagination, filtering)
- `GET /api/v1/{resource}/{id}` - Get single record
- `POST /api/v1/{resource}` - Create new record
- `PUT /api/v1/{resource}/{id}` - Update record
- `DELETE /api/v1/{resource}/{id}` - Delete record

## URLs & Ports

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432
- **Keycloak**: http://localhost:8080

## Feature List (15 Total)

Development priority order:
1. Users (foundation for all features)
2. Schools (multi-tenant foundation)
3. Teachers (required for classes)
4. Students (core entity)
5. Parents (family relationships)
6. Subjects (curriculum foundation)
7. Rooms (facility management)
8. Classes (teacher-subject-student assignments)
9. Lessons (lesson planning)
10. Assessments (grading and evaluation)
11. Attendance (daily tracking)
12. Events (school calendar)
13. Activities (extracurricular)
14. Vendors (external relationships)
15. Merits (reward system)

Each feature has a detailed plan in `docs/features/[feature-name]-plan.md`
