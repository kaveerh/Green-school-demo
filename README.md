# Green School Management System
**A comprehensive digital platform for primary school administration (Grades 1-7)**

## Project Status
**Phase**: Planning & Documentation Complete
**Ready For**: Development Start

## Quick Start

### For Claude Code
Start here: Read `CLAUDE.md` for complete development guidance.

### For Developers
1. Read `CLAUDE.md` - Project overview and development commands
2. Review `docs/MASTER_FEATURE_PLAN.md` - Feature development roadmap
3. Start with Feature 01 (Users) - See `docs/features/01-users-plan.md`
4. Use `docs/DEVELOPMENT_CHECKLIST.md` for each feature implementation

## Documentation Structure

```
claude-projects/
├── CLAUDE.md                              # Main guidance for Claude Code
├── README.md                              # This file
└── docs/
    ├── MASTER_FEATURE_PLAN.md            # Overall development plan
    ├── DEVELOPMENT_CHECKLIST.md          # Per-feature checklist template
    ├── features/
    │   ├── 01-users-plan.md              # Detailed: Users feature
    │   ├── 02-schools-plan.md            # Detailed: Schools feature
    │   └── ALL_FEATURES_SUMMARY.md       # Summary of all 15 features
    ├── api/
    │   └── API_ROUTES_MASTER.md          # Complete API reference
    ├── schema/                            # Database schemas (to be created per feature)
    ├── ux/                                # UX flow documentation (to be created per feature)
    └── plans/                             # Additional planning docs
```

## Technology Stack

### Frontend
- Vue 3 + TypeScript + Vite
- Pinia (state management)
- Vue Router 3
- Tailwind CSS
- Headless UI
- Playwright (testing)

### Backend
- Python API + TypeScript
- PostgreSQL with Row Level Security
- SQLAlchemy ORM
- express-validator
- pytest (testing)

### Authentication
- Keycloak
- Realm: Green-School-id
- Test User: admin@greenschool.edu / Password123

### Infrastructure
- Docker containers (Frontend, Backend, Database)
- Ports: 3000 (Frontend), 8000 (Backend), 5432 (Database), 8080 (Keycloak)

## Features (15 Total)

### Phase 1: Foundation (Weeks 1-3)
1. ✅ **Users** - Multi-persona authentication system
2. ✅ **Schools** - Multi-tenant foundation

### Phase 2: Core Entities (Weeks 4-7)
3. ⬜ **Teachers** - Teacher management and assignments
4. ⬜ **Students** - Student profiles and grade management
5. ⬜ **Parents** - Parent profiles and child relationships

### Phase 3: Academic Structure (Weeks 8-11)
6. ⬜ **Subjects** - Curriculum management
7. ⬜ **Rooms** - Facility and resource management
8. ⬜ **Classes** - Class creation and enrollment

### Phase 4: Academic Operations (Weeks 12-15)
9. ⬜ **Lessons** - Lesson planning
10. ⬜ **Assessments** - Grading and evaluation
11. ⬜ **Attendance** - Attendance tracking

### Phase 5: Extended Features (Weeks 16-20)
12. ⬜ **Events** - School calendar
13. ⬜ **Activities** - Extracurricular activities
14. ⬜ **Vendors** - Vendor management
15. ⬜ **Merits** - Student reward system

**Legend**: ✅ Complete | 🟡 In Progress | ⬜ Not Started

## Key Principles

### 1. Sequential Development
Build ONE feature at a time, completing all phases before moving to the next.

### 2. Full CRUD Implementation
Every feature must have complete Create, Read, List, Update, Delete operations.

### 3. Multi-Tenant Isolation
All data segregated by school_id with Row Level Security policies.

### 4. GDPR/POPPI Compliance
- Audit logging for all CRUD operations
- Soft delete for data retention
- Parental consent tracking
- Right to deletion support

### 5. Quality Gates
Each feature must pass all quality gates before proceeding:
- Database schema documented
- All CRUD endpoints working
- Test coverage >80%
- Responsive UI on all devices
- Documentation complete

## Development Workflow

For each feature, follow this 15-phase workflow:

1. **Planning & Review** (1-2 hours)
2. **Database Design** (2-4 hours)
3. **ORM Models** (1-2 hours)
4. **Repository Layer** (1-2 hours)
5. **Service Layer** (2-3 hours)
6. **API Controller** (2-3 hours)
7. **Backend Testing** (2-3 hours)
8. **Frontend Store** (2-3 hours)
9. **Frontend API Service** (1-2 hours)
10. **Frontend Components** (4-6 hours)
11. **Frontend Routing** (1 hour)
12. **E2E Testing** (2-4 hours)
13. **Docker Integration** (1-2 hours)
14. **Documentation** (1-2 hours)
15. **Final Review** (1 hour)

**Average Time Per Feature**: 25-40 hours

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)
- PostgreSQL 14+ (or use Docker)

### Initial Setup (When Ready)
```bash
# Clone repository (when created)
git clone <repository-url>
cd claude-projects

# Start infrastructure with Docker
docker-compose up -d

# Access applications
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Keycloak: http://localhost:8080
```

### Development Commands

See `CLAUDE.md` for complete commands reference including:
- Docker commands
- Frontend commands (Vue)
- Backend commands (Python)
- Database commands (PostgreSQL)
- Testing commands (pytest, Playwright)

## API Documentation

Complete API reference available in `docs/api/API_ROUTES_MASTER.md`

- Base URL: http://localhost:8000/api/v1
- Authentication: Keycloak Bearer Token
- All endpoints require authentication (except password reset)
- Multi-tenant via X-School-ID header

## Current Status

### ✅ Completed
- Project structure initialized
- Documentation framework created
- CLAUDE.md guidance file
- Master feature plan
- Development checklist template
- Detailed plans for Users and Schools features
- Summary of all 15 features
- Complete API routes documentation

### 🎯 Next Steps
1. Review all documentation
2. Initialize Git repository
3. Set up Docker environment
4. Create initial project scaffolding
5. Begin Feature 01: Users
   - Start with database schema
   - Follow development checklist
   - Complete all 15 phases
   - Pass all quality gates
6. Move to Feature 02: Schools

## Timeline

**Estimated Total Time**: 425-533 hours (11-14 weeks at 40 hours/week)

- Phase 1 (Foundation): 2-3 weeks
- Phase 2 (Core Entities): 3-4 weeks
- Phase 3 (Academic Structure): 3-4 weeks
- Phase 4 (Academic Operations): 3-4 weeks
- Phase 5 (Extended Features): 4-5 weeks

## Key Business Rules

- **Grades**: System supports ONLY Grades 1-7
- **Quarters**: Academic year divided into Q1, Q2, Q3, Q4
- **Multi-Tenancy**: Complete data isolation between schools
- **GDPR**: Parental consent required for student data
- **Roles**: Administrator, Teacher, Student, Parent, Vendor
- **Soft Delete**: All deletions maintain audit trail

## Testing Strategy

### Backend (pytest)
- Unit tests for repositories
- Unit tests for services
- Integration tests for API endpoints
- Multi-tenant isolation tests
- Target coverage: >80%

### Frontend (Playwright)
- E2E tests for CRUD flows
- Validation error tests
- Responsive design tests (mobile/tablet/desktop)
- Authorization tests

### Docker
- Full integration tests in containerized environment
- Migration tests
- Data seed tests

## Architecture Highlights

### Backend Layers
- **Models**: SQLAlchemy ORM definitions
- **Repositories**: Data access layer
- **Services**: Business logic layer
- **Controllers**: HTTP request handlers
- **Schemas**: Input/output validation

### Frontend Structure
- **Components**: Reusable Vue components
- **Views**: Page-level components
- **Stores**: Pinia stores per feature
- **Services**: API integration layer
- **Router**: Route definitions with guards

### Database
- **14 Core Tables**: Complete relational schema
- **UUID Primary Keys**: Distributed system support
- **Audit Fields**: created_at, updated_at, created_by, updated_by
- **Soft Delete**: deleted_at, deleted_by
- **RLS Policies**: Enforce multi-tenancy

## Support & Resources

### Documentation
- `CLAUDE.md` - Main development guide
- `docs/MASTER_FEATURE_PLAN.md` - Development roadmap
- `docs/DEVELOPMENT_CHECKLIST.md` - Implementation checklist
- `docs/api/API_ROUTES_MASTER.md` - API reference
- `docs/features/*.md` - Per-feature plans

### Key URLs (When Running)
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432
- Keycloak: http://localhost:8080

### Authentication Test Credentials
- Email: admin@greenschool.edu
- Password: Password123
- Role: Administrator

## Contributing

When implementing features:
1. Read the feature plan in `docs/features/`
2. Copy `docs/DEVELOPMENT_CHECKLIST.md` for the feature
3. Follow all 15 phases sequentially
4. Check off each task as completed
5. Pass all quality gates before proceeding
6. Update progress in master plan
7. Commit frequently with clear messages

## License

[To be determined]

## Authors

[To be determined]

---

**Last Updated**: 2025-10-13
**Documentation Version**: 1.0
**Project Phase**: Planning Complete, Ready for Development
