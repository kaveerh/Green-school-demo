# Build Guide
**Status**: Infrastructure Started - Continue Building
**Date**: 2025-10-13

## What's Been Completed ✅

### 1. Project Initialization
- ✅ Git repository initialized with first commit
- ✅ Complete documentation (5,615+ lines)
- ✅ `.gitignore` configured
- ✅ `.env.example` created

### 2. Docker Infrastructure
- ✅ `docker-compose.yml` created with 4 services:
  - PostgreSQL database (port 5432)
  - Keycloak authentication (port 8080)
  - Backend API (port 8000)
  - Frontend (port 3000)

### 3. Backend Structure Started
- ✅ `requirements.txt` with FastAPI, SQLAlchemy, etc.
- ✅ `Dockerfile` for Python backend
- ✅ Directory structure created (models, repositories, services, controllers, etc.)
- ✅ `main.py` FastAPI app with health check
- ✅ `config/settings.py` Pydantic settings
- ✅ `config/database.py` SQLAlchemy async setup

### 4. Still Needed
- ⬜ Frontend Vue 3 project initialization
- ⬜ Keycloak realm configuration
- ⬜ Database migrations
- ⬜ Feature 01 (Users) implementation
- ⬜ All remaining 14 features

---

## Next Steps - Continue Building

### Phase 1: Complete Infrastructure Setup (2-4 hours)

#### Step 1: Create Frontend Project Structure
```bash
cd /Users/kaveerh/claude-projects/frontend

# Create package.json
cat > package.json << 'EOF'
{
  "name": "greenschool-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "playwright test",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore"
  },
  "dependencies": {
    "vue": "^3.4.15",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "keycloak-js": "^23.0.4",
    "@headlessui/vue": "^1.7.17",
    "@heroicons/vue": "^2.1.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.3",
    "vite": "^5.0.11",
    "vue-tsc": "^1.8.27",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "@playwright/test": "^1.41.1",
    "eslint": "^8.56.0",
    "@typescript-eslint/eslint-plugin": "^6.19.1",
    "@typescript-eslint/parser": "^6.19.1",
    "eslint-plugin-vue": "^9.20.1"
  }
}
EOF

# Create vite.config.ts
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    host: true
  }
})
EOF

# Create tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
EOF

# Create directory structure
mkdir -p src/{components/{base,layout,features,common},views,stores,services,composables,router,types,utils,assets/{css,images}}

# Create main.ts
cat > src/main.ts << 'EOF'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/css/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
EOF

# Create App.vue
cat > src/App.vue << 'EOF'
<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>
EOF

# Create index.html
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Green School Management System</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
EOF

# Create Tailwind CSS config
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          700: '#0369a1',
        }
      }
    },
  },
  plugins: [],
}
EOF

# Create PostCSS config
cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# Create main CSS
cat > src/assets/css/main.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# Install dependencies
npm install
```

#### Step 2: Configure Keycloak
```bash
cd /Users/kaveerh/claude-projects/keycloak

# Create realm export file
cat > realm-export.json << 'EOF'
{
  "realm": "Green-School-id",
  "enabled": true,
  "sslRequired": "none",
  "registrationAllowed": false,
  "loginWithEmailAllowed": true,
  "duplicateEmailsAllowed": false,
  "resetPasswordAllowed": true,
  "editUsernameAllowed": false,
  "bruteForceProtected": true,
  "clients": [
    {
      "clientId": "Green-School-id",
      "enabled": true,
      "publicClient": true,
      "redirectUris": [
        "http://localhost:3000/*",
        "http://localhost/*"
      ],
      "webOrigins": [
        "http://localhost:3000",
        "http://localhost"
      ],
      "directAccessGrantsEnabled": true,
      "standardFlowEnabled": true,
      "implicitFlowEnabled": false
    }
  ],
  "users": [
    {
      "username": "admin@greenschool.edu",
      "email": "admin@greenschool.edu",
      "enabled": true,
      "emailVerified": true,
      "firstName": "Admin",
      "lastName": "User",
      "credentials": [
        {
          "type": "password",
          "value": "Password123",
          "temporary": false
        }
      ],
      "realmRoles": ["admin"]
    }
  ],
  "roles": {
    "realm": [
      {
        "name": "admin",
        "description": "Administrator role"
      },
      {
        "name": "teacher",
        "description": "Teacher role"
      },
      {
        "name": "student",
        "description": "Student role"
      },
      {
        "name": "parent",
        "description": "Parent role"
      },
      {
        "name": "vendor",
        "description": "Vendor role"
      }
    ]
  }
}
EOF
```

#### Step 3: Create Initial Database Migration
```bash
cd /Users/kaveerh/claude-projects/backend/migrations

# Create schools table migration (prerequisite for users)
cat > 001_create_schools.sql << 'EOF'
-- Migration: 001_create_schools.sql
-- Description: Create schools table (multi-tenant foundation)

BEGIN;

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

-- Insert test school
INSERT INTO schools (name, slug, email, phone, city, state)
VALUES (
    'Green Valley Elementary',
    'green-valley',
    'admin@greenschool.edu',
    '+1-555-0100',
    'Springfield',
    'CA'
);

COMMIT;
EOF

# Create users table migration
cat > 002_create_users.sql << 'EOF'
-- Migration: 002_create_users.sql
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

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for school isolation
CREATE POLICY users_school_isolation ON users
    USING (school_id = current_setting('app.current_school_id', true)::UUID);

COMMIT;
EOF
```

### Phase 2: Start Docker Services (30 minutes)
```bash
cd /Users/kaveerh/claude-projects

# Create .env file from example
cp .env.example .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify services are running
docker-compose ps

# Access services:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000/docs
# - Keycloak: http://localhost:8080
# - Database: localhost:5432
```

### Phase 3: Implement Feature 01 - Users (32-40 hours)

Follow the 15-phase workflow from `docs/DEVELOPMENT_CHECKLIST.md`:

1. **Planning & Review** - Read `docs/features/01-users-plan.md`
2. **Database Design** - Already done in migrations above
3. **ORM Models** - Create `backend/models/user.py`
4. **Repository Layer** - Create `backend/repositories/user_repository.py`
5. **Service Layer** - Create `backend/services/user_service.py`
6. **API Controller** - Create `backend/controllers/user_controller.py`
7. **Backend Testing** - Create `backend/tests/test_users.py`
8. **Frontend Store** - Create `frontend/src/stores/userStore.ts`
9. **Frontend API Service** - Create `frontend/src/services/userService.ts`
10. **Frontend Components** - Create Vue components
11. **Frontend Routing** - Add routes to `frontend/src/router/index.ts`
12. **E2E Testing** - Create Playwright tests
13. **Docker Integration** - Test in Docker
14. **Documentation** - Update docs
15. **Final Review** - Pass all quality gates

### Phase 4: Repeat for Features 02-15

After completing Users, move to Schools, then Teachers, Students, Parents, etc., following the same 15-phase workflow.

---

## Quick Commands Reference

### Docker
```bash
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs -f        # View logs
docker-compose ps             # List services
docker-compose restart        # Restart all services
```

### Backend
```bash
cd backend
pip install -r requirements.txt      # Install dependencies
uvicorn main:app --reload            # Run dev server
pytest                               # Run tests
black .                              # Format code
flake8                               # Lint code
```

### Frontend
```bash
cd frontend
npm install                   # Install dependencies
npm run dev                   # Run dev server
npm run build                 # Build for production
npm run test                  # Run Playwright tests
npm run lint                  # Lint code
```

### Database
```bash
# Connect to database
docker exec -it greenschool-db psql -U postgres -d greenschool

# Run migrations
docker exec -i greenschool-db psql -U postgres -d greenschool < backend/migrations/001_create_schools.sql
docker exec -i greenschool-db psql -U postgres -d greenschool < backend/migrations/002_create_users.sql

# Backup database
docker exec greenschool-db pg_dump -U postgres greenschool > backup.sql
```

---

## Progress Tracking

Update `docs/MASTER_FEATURE_PLAN.md` after completing each feature:

| # | Feature | Status | DB | API | UX | Tests | Docs | Complete |
|---|---------|--------|----|----|-----|-------|------|----------|
| 1 | Users | In Progress | 🟡 | ⬜ | ⬜ | ⬜ | ⬜ | 20% |
| 2 | Schools | Not Started | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 0% |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## Resources

- **Documentation**: All docs in `docs/` directory
- **Feature Plans**: `docs/features/`
- **API Reference**: `docs/api/API_ROUTES_MASTER.md`
- **Database Schema**: `docs/schema/DATABASE_SCHEMA_OVERVIEW.md`
- **UX Design System**: `docs/ux/UX_DESIGN_SYSTEM.md`

---

## Support

If you encounter issues:
1. Check `CLAUDE.md` for guidance
2. Review relevant feature plan in `docs/features/`
3. Check Docker logs: `docker-compose logs -f`
4. Verify all services are running: `docker-compose ps`
5. Check database connection: `docker exec greenschool-db pg_isready`

---

**Status**: Ready to Continue Building
**Next Action**: Complete frontend setup, start Docker, implement Feature 01
