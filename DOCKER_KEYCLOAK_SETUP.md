# Docker Keycloak Setup with Auto-Configuration

## What Changed

I've updated the Docker Compose configuration to:

1. **Add Keycloak container** to docker-compose.yml
2. **Auto-configure realm** with all users and CORS settings
3. **Fix CORS issues** by including web origins in the realm config
4. **Enable auto-import** of realm configuration on startup

## Changes Made

### 1. Added Keycloak Service to `docker-compose.yml`
- Container: `greenschool-keycloak`
- Port: `8080:8080`
- Image: Keycloak 23.0 (latest LTS)
- Mode: Development mode (`start-dev`)
- Auto-import enabled

### 2. Created Realm Configuration File
**File**: `/keycloak/green-school-id-realm.json`

This file includes:
- ✅ Realm: `green-school-id`
- ✅ Client: `green-school-id` with CORS enabled
- ✅ Roles: administrator, teacher, parent, student, vendor
- ✅ 4 Test users with credentials
- ✅ Web Origins set to `+` (auto-allow all redirect URIs)

### 3. Updated Backend Configuration
- Changed `KEYCLOAK_URL` from `host.docker.internal:8080` to `keycloak:8080`
- Backend now references Keycloak by container name
- Added CORS origins with wildcard: `http://localhost:3000/*`

## Setup Instructions

### Step 1: Stop Existing Services

If you have Keycloak running externally (not in Docker), **stop it first**:

```bash
# If Keycloak is running as a service
sudo systemctl stop keycloak

# If running in standalone mode, press Ctrl+C in the terminal

# Or if running in another Docker container
docker stop <keycloak-container-name>
```

### Step 2: Stop Current Docker Containers

```bash
cd /Users/kaveerh/claude-projects
docker-compose down
```

This will stop all containers but keep the data.

### Step 3: Start Services with New Configuration

```bash
docker-compose up -d
```

This will:
1. Pull the Keycloak image (first time only - ~2 minutes)
2. Start all services (database, keycloak, backend, frontend)
3. Auto-import the realm configuration
4. Wait for health checks to pass

### Step 4: Wait for Keycloak Initialization

Keycloak takes about 60-90 seconds to start up. Monitor the logs:

```bash
docker-compose logs -f keycloak
```

**Look for these messages:**
```
Added user 'admin' to realm 'master'
Importing realm from file green-school-id-realm.json
Realm green-school-id imported
Keycloak 23.0 started in 45s
Listening on: http://0.0.0.0:8080
```

Press `Ctrl+C` to stop watching logs (containers keep running).

### Step 5: Verify Services are Running

```bash
docker-compose ps
```

**Expected output:**
```
NAME                    STATUS
greenschool-backend     Up 30 seconds (healthy)
greenschool-db          Up 30 seconds (healthy)
greenschool-frontend    Up 30 seconds
greenschool-keycloak    Up 30 seconds (healthy)
```

All services should show "Up" and "(healthy)".

### Step 6: Verify Keycloak Configuration

**Test Keycloak is accessible:**
```bash
curl http://localhost:8080/realms/green-school-id/.well-known/openid-configuration | jq .issuer
```

**Expected output:**
```json
"http://localhost:8080/realms/green-school-id"
```

**Access Keycloak Admin Console:**
1. Open: http://localhost:8080/admin
2. Login with:
   - **Username**: `admin`
   - **Password**: `admin`
3. Select realm: **green-school-id** (dropdown in top-left)
4. Verify:
   - Clients → green-school-id exists
   - Users → 4 users exist (admin, teacher, parent, student)
   - Roles → 5 roles exist

### Step 7: Test Authentication Flow

1. **Open the frontend**:
   ```
   http://localhost:3000
   ```

2. **Open Browser DevTools** (F12) → Console tab

3. **Click "Sign In"**

4. **Expected console output:**
   ```
   🔐 Initializing Keycloak authentication...
   🔄 Initializing Keycloak...
   User is not authenticated
   ℹ️ User is not authenticated
   ✓ Auth initialization complete. Authenticated: false
   ```

5. **Login with test credentials**:
   - Email: `admin@greenschool.edu`
   - Password: `Admin123`

6. **Expected console output after login:**
   ```
   🔄 Initializing Keycloak...
   User is authenticated
   👤 User profile loaded: admin@greenschool.edu administrator
   ✅ Keycloak authentication successful: Admin User (administrator)
   🏫 Available schools: 1
   ✓ Auth initialization complete. Authenticated: true
   ```

7. **Verify UI updates:**
   - ✅ Loading screen appears briefly
   - ✅ Navigation sidebar shows "Admin User"
   - ✅ User menu shows "administrator" role
   - ✅ Dashboard loads successfully
   - ✅ School selector appears

### Step 8: Test Different User Roles

Logout and login with different accounts:

| Email | Password | Role | Expected Access |
|-------|----------|------|----------------|
| admin@greenschool.edu | Admin123 | administrator | Full access to all menu items |
| teacher@greenschool.edu | Admin123 | teacher | Classes, Lessons, Assessments, Attendance |
| parent@greenschool.edu | Admin123 | parent | View children's data only |
| student@greenschool.edu | Admin123 | student | View own data only |

## Troubleshooting

### Issue: Keycloak container won't start

**Check logs:**
```bash
docker-compose logs keycloak
```

**Common causes:**
- Port 8080 already in use (stop external Keycloak)
- Not enough memory (Keycloak needs ~512MB)

**Solution:**
```bash
# Check what's using port 8080
lsof -i :8080

# Stop the process using the port
kill -9 <PID>

# Restart
docker-compose up -d keycloak
```

### Issue: "Realm not found" error

**Cause:** Realm import failed

**Solution:**
1. Check the realm file exists:
   ```bash
   ls -la keycloak/green-school-id-realm.json
   ```

2. Verify file is mounted in container:
   ```bash
   docker exec greenschool-keycloak ls /opt/keycloak/data/import
   ```

3. Re-import manually:
   ```bash
   docker-compose restart keycloak
   docker-compose logs -f keycloak
   ```

### Issue: CORS error persists

**Check client configuration:**
1. Go to: http://localhost:8080/admin
2. Login: admin/admin
3. Select realm: green-school-id
4. Clients → green-school-id → Settings
5. Verify:
   - Web Origins: `+` or `http://localhost:3000`
   - Valid Redirect URIs: `http://localhost:3000/*`

**If configuration is wrong, the realm import failed. Fix:**
```bash
# Remove Keycloak data and reimport
docker-compose down -v
docker volume rm claude-projects_keycloak_data
docker-compose up -d
```

### Issue: Users don't exist

**Create users manually:**
1. Go to: http://localhost:8080/admin
2. Select realm: green-school-id
3. Users → Add User
4. Fill in details (see realm JSON for reference)
5. Credentials tab → Set password (temporary=OFF)
6. Role Mappings tab → Assign realm role

### Issue: Backend can't reach Keycloak

**Check network connectivity:**
```bash
docker exec greenschool-backend curl http://keycloak:8080/realms/green-school-id/.well-known/openid-configuration
```

**If it fails:**
```bash
docker-compose restart backend
```

### Issue: Frontend shows blank page

**Check browser console** for errors.

**Common fixes:**
1. Clear browser cache: `Ctrl+Shift+Delete`
2. Hard refresh: `Ctrl+Shift+R`
3. Try incognito mode
4. Check frontend logs:
   ```bash
   docker-compose logs frontend
   ```

## Service URLs

After setup is complete:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Keycloak Admin**: http://localhost:8080/admin
- **Keycloak Realm**: http://localhost:8080/realms/green-school-id
- **PostgreSQL**: localhost:5432

## Keycloak Admin Access

- **URL**: http://localhost:8080/admin
- **Username**: `admin`
- **Password**: `admin`
- **Realm to select**: `green-school-id`

## Test User Credentials

All test users have the same password: `Admin123`

| Email | Role | Full Name |
|-------|------|-----------|
| admin@greenschool.edu | administrator | Admin User |
| teacher@greenschool.edu | teacher | Teacher User |
| parent@greenschool.edu | parent | Parent User |
| student@greenschool.edu | student | Student User |

## Useful Commands

**View all logs:**
```bash
docker-compose logs -f
```

**View specific service logs:**
```bash
docker-compose logs -f keycloak
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Restart a specific service:**
```bash
docker-compose restart keycloak
docker-compose restart backend
docker-compose restart frontend
```

**Check service health:**
```bash
docker-compose ps
```

**Stop all services:**
```bash
docker-compose down
```

**Stop all services and remove volumes (DANGER - deletes data):**
```bash
docker-compose down -v
```

**Rebuild containers:**
```bash
docker-compose up -d --build
```

## What's Next

After successful setup:

1. ✅ Test login with all 4 user roles
2. ✅ Verify menu filtering by role
3. ✅ Test navigation between pages
4. ✅ Test logout functionality
5. ✅ Test page refresh (stays authenticated)

The CORS issue is now fixed because:
- Keycloak runs in the same Docker network
- Realm configuration includes `webOrigins: ["+"]`
- This automatically allows CORS from all redirect URIs
- No manual Keycloak configuration needed!
