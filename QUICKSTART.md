# Quick Start Guide
**Get the Green School Management System running in 15 minutes**

## Prerequisites
✅ Docker and Docker Compose installed
✅ Node.js 20+ installed
✅ Keycloak running on http://localhost:8080
   - Realm: `green-school-id`
   - Client: `green-school-id`
   - Test user: `admin@greenschool.edu` / `Admin123`

---

## Step 1: Install Frontend Dependencies (2 minutes)

```bash
cd /Users/kaveerh/claude-projects/frontend
npm install
cp .env.example .env
cd ..
```

---

## Step 2: Start Database & Run Migrations (3 minutes)

```bash
# Start PostgreSQL
docker-compose up -d database

# Wait for database to be ready (check logs)
docker-compose logs database

# Run migrations
docker exec -i greenschool-db psql -U postgres -d greenschool < backend/migrations/001_create_schools.sql
docker exec -i greenschool-db psql -U postgres -d greenschool < backend/migrations/002_create_users.sql

# Verify tables created
docker exec -it greenschool-db psql -U postgres -d greenschool -c "\dt"
```

Expected output:
```
           List of relations
 Schema |  Name   | Type  |  Owner
--------+---------+-------+----------
 public | schools | table | postgres
 public | users   | table | postgres
```

---

## Step 3: Start Backend & Frontend (2 minutes)

```bash
# Start all remaining services
docker-compose up -d

# Check services are running
docker-compose ps
```

Expected output:
```
NAME                     STATUS    PORTS
greenschool-backend      Up        0.0.0.0:8000->8000/tcp
greenschool-db           Up        0.0.0.0:5432->5432/tcp
greenschool-frontend     Up        0.0.0.0:3000->3000/tcp
```

---

## Step 4: Verify Everything Works (5 minutes)

### Test Database
```bash
docker exec -it greenschool-db psql -U postgres -d greenschool

# Check school
SELECT * FROM schools;

# Check users
SELECT email, first_name, last_name, persona FROM users;

# Exit
\q
```

### Test Backend API
Open browser: http://localhost:8000/docs

You should see Swagger UI with API documentation.

Test the health endpoint:
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-13T...",
  "environment": "development",
  "version": "1.0.0"
}
```

### Test Frontend
Open browser: http://localhost:3000

You should see:
- Welcome page with "Green School Management System" title
- Links to Dashboard and API Docs
- Modern gradient background

Click "Go to Dashboard" - you should see:
- Navigation bar
- Stats cards (all showing 0)
- Quick action buttons
- Blue info banner about infrastructure being complete

---

## Step 5: Verify Keycloak Integration (3 minutes)

### Check Keycloak
Open: http://localhost:8080

Login with: `admin@greenschool.edu` / `Admin123`

Verify:
- Realm: `green-school-id` exists
- Client: `green-school-id` is configured
- User exists with correct credentials

### Get OpenID Configuration
```bash
curl http://localhost:8080/realms/green-school-id/.well-known/openid-configuration | jq
```

This should return Keycloak's OpenID Connect configuration.

---

## 🎉 Success! You're Running!

### What's Working
✅ PostgreSQL database with 2 tables (schools, users)
✅ Test data: 1 school, 5 users (all personas)
✅ Backend API with health check
✅ Frontend Vue 3 app with routing
✅ Keycloak authentication ready
✅ Docker containers running smoothly

### Accessible URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Database**: localhost:5432 (use psql or pgAdmin)
- **Keycloak**: http://localhost:8080

### Test Credentials
**Admin User**:
- Email: `admin@greenschool.edu`
- Password: `Admin123`

---

## Next Steps: Implement Features

### Feature 01: Users (Next!)
Follow the 15-phase workflow in `docs/DEVELOPMENT_CHECKLIST.md`:

1. ✅ Planning - Read `docs/features/01-users-plan.md`
2. ✅ Database - Already created in migration 002
3. ⬜ ORM Models - Create `backend/models/user.py`
4. ⬜ Repository - Create `backend/repositories/user_repository.py`
5. ⬜ Service - Create `backend/services/user_service.py`
6. ⬜ Controller - Create `backend/controllers/user_controller.py`
7. ⬜ Tests - Create `backend/tests/test_users.py`
8. ⬜ Frontend Store - Create `frontend/src/stores/userStore.ts`
9. ⬜ Frontend Service - Create `frontend/src/services/userService.ts`
10. ⬜ Frontend UI - Create Vue components
11. ⬜ Routing - Add routes
12. ⬜ E2E Tests - Playwright
13. ⬜ Docker Test - Verify in containers
14. ⬜ Documentation - Update docs
15. ⬜ Review - Pass quality gates

### Detailed Instructions
See `docs/features/01-users-plan.md` for complete specifications.

---

## Troubleshooting

### Database won't start
```bash
# Check logs
docker-compose logs database

# Remove and recreate
docker-compose down -v
docker-compose up -d database
```

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issue: Python dependencies
docker-compose build backend
docker-compose up -d backend
```

### Frontend won't start
```bash
# Check logs
docker-compose logs frontend

# Common issue: node_modules
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..
docker-compose restart frontend
```

### Migrations fail
```bash
# Check if database is ready
docker exec -it greenschool-db pg_isready

# Connect and check manually
docker exec -it greenschool-db psql -U postgres -d greenschool

# Rerun migrations
docker exec -i greenschool-db psql -U postgres -d greenschool < backend/migrations/001_create_schools.sql
```

### Keycloak connection issues
Make sure Keycloak is running and accessible:
```bash
curl http://localhost:8080/realms/green-school-id/.well-known/openid-configuration
```

Backend connects to Keycloak via `host.docker.internal:8080` (inside container).

---

## Useful Commands

### Docker
```bash
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose ps                 # List services
docker-compose logs -f            # View logs (all services)
docker-compose logs -f backend    # View backend logs only
docker-compose restart backend    # Restart backend
docker-compose build backend      # Rebuild backend
```

### Database
```bash
# Connect to database
docker exec -it greenschool-db psql -U postgres -d greenschool

# Run SQL file
docker exec -i greenschool-db psql -U postgres -d greenschool < file.sql

# Backup database
docker exec greenschool-db pg_dump -U postgres greenschool > backup.sql

# Restore database
docker exec -i greenschool-db psql -U postgres -d greenschool < backup.sql
```

### Backend
```bash
# Install dependencies (if not using Docker)
cd backend
pip install -r requirements.txt

# Run dev server locally
python -m uvicorn main:app --reload --port 8000

# Run tests
pytest

# Format code
black .
```

### Frontend
```bash
# Install dependencies
cd frontend
npm install

# Run dev server locally
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

---

## Documentation Reference

- **Main Guide**: `CLAUDE.md`
- **Project Status**: `STATUS.md`
- **Build Guide**: `BUILD_GUIDE.md`
- **Feature Plans**: `docs/features/`
- **API Reference**: `docs/api/API_ROUTES_MASTER.md`
- **Database Schema**: `docs/schema/DATABASE_SCHEMA_OVERVIEW.md`
- **UX Design**: `docs/ux/UX_DESIGN_SYSTEM.md`

---

**Status**: 🟢 Infrastructure Complete - Ready for Feature Development
**Progress**: 20% Complete
**Next**: Implement Feature 01: Users (follow DEVELOPMENT_CHECKLIST.md)
