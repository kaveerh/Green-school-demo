# Navigation Not Working After Login - Debug Guide

## Problem
You can login successfully, but after logging in, the navigation doesn't work to access any features.

## Debug Steps

### Step 1: Access the Debug Page

After logging in, navigate to the debug page:

```
http://localhost:3000/debug
```

This page will show you:
- ✅ Authentication state (is user authenticated?)
- ✅ User information (email, name, persona, roles)
- ✅ School context
- ✅ Role checks (administrator, teacher, etc.)
- ✅ Keycloak token information
- ✅ Current route information

### Step 2: Check Console Logs

1. Open Browser DevTools (F12)
2. Go to Console tab
3. Look for these messages after login:

**Expected Success Messages:**
```
🔐 Initializing Keycloak authentication...
🔄 Initializing Keycloak...
User is authenticated
👤 User profile loaded: admin@greenschool.edu administrator
✅ Keycloak authentication successful: Admin User (administrator)
🏫 Available schools: 1
✓ Auth initialization complete. Authenticated: true
🧭 Navigating to: /dashboard, Requires Auth: true, Is Authenticated: true
```

**Look for Error Messages:**
- CORS errors
- Token parsing errors
- Role assignment issues
- Navigation guard blocks

### Step 3: Verify User Roles in Keycloak

1. Open Keycloak Admin Console:
   ```
   http://localhost:8080/admin
   ```

2. Login with admin credentials

3. Select realm: **green-school-id**

4. Go to: **Users** → Find your test user (e.g., admin@greenschool.edu)

5. Click on the user → **Role Mappings** tab

6. **Verify:**
   - Under "Realm Roles" section
   - The user should have the appropriate role assigned (e.g., "administrator")
   - Check "Effective Roles" to see all assigned roles

### Step 4: Test Navigation Manually

From the debug page, try clicking the test navigation links:
- Go to Dashboard
- Go to Users
- Go to Students
- Go to Classes

**If these work:**
- The issue is with the sidebar navigation component
- Role filtering might be too restrictive

**If these don't work:**
- The issue is with router guards or authentication state
- Check console for navigation errors

## Common Issues and Solutions

### Issue 1: No Roles Assigned in Keycloak

**Symptom:** Debug page shows `Roles: None` or empty roles array

**Solution:**
1. Go to Keycloak Admin Console
2. Users → Select your user
3. Role Mappings tab
4. Assign the appropriate role (administrator, teacher, parent, or student)
5. Logout and login again

### Issue 2: Menu Items Not Showing

**Symptom:** Sidebar is empty or only shows Dashboard

**Solution:**
This happens when role checks fail. Verify:

1. **In Debug page:**
   - Check "Role Checks" section
   - All should show `true` for administrator

2. **If all show `false`:**
   - Roles are not being read from Keycloak token
   - Check Keycloak token in debug page
   - Look for `realm_access.roles` array

3. **Fix:**
   ```bash
   # Verify Keycloak configuration
   curl http://localhost:8080/realms/green-school-id/.well-known/openid-configuration
   ```

### Issue 3: Router Navigation Blocked

**Symptom:** Clicking links does nothing or redirects back

**Check Console for:**
```
🔒 Route requires authentication, redirecting to login
⛔ User does not have required role: ['administrator']
```

**Solution:**
- If redirecting to login: Token expired or not set
- If blocked by role: Role assignment issue in Keycloak

### Issue 4: Navigation Links Active but Page Not Loading

**Symptom:** URL changes but page stays the same

**Possible Causes:**
1. Component import errors
2. Route configuration issues
3. Missing components

**Check:**
```bash
# Check frontend logs for import errors
docker-compose logs frontend | grep -i error
```

### Issue 5: School Context Not Set

**Symptom:** Debug page shows "Selected School: None"

**Impact:** Some routes require school context

**Solution:**
1. Check if schools are fetched: `Available Schools: > 0`
2. If 0 schools:
   - Backend API might not be returning schools
   - Test: `curl http://localhost:8000/api/v1/schools?page=1&limit=10`
3. If schools available but none selected:
   - Should auto-select first school
   - Check console for errors during school fetch

## Testing Different Roles

Test with each persona to see what navigation items appear:

### Administrator
Should see ALL menu items:
- Dashboard
- Users
- Schools
- Teachers
- Students
- Parents
- Subjects
- Rooms
- Classes
- Lessons
- Assessments
- Attendance
- Events
- Activities
- Vendors
- Merits

### Teacher
Should see:
- Dashboard
- Students
- Parents
- Subjects
- Rooms
- Classes
- Lessons
- Assessments
- Attendance
- Events
- Activities
- Merits

### Parent/Student
Should see limited items:
- Dashboard
- (Their specific views)

## Manual Role Check Test

Open Browser Console and run:

```javascript
// Check if auth store is accessible
const authStore = window.$app.config.globalProperties.$pinia._s.get('auth')

// Check authentication
console.log('Is Authenticated:', authStore.isAuthenticated)
console.log('Current User:', authStore.currentUser)
console.log('Roles:', authStore.currentUser?.roles)
console.log('Has Admin Role:', authStore.hasRole('administrator'))
```

## Quick Fixes

### Fix 1: Clear Browser Cache and Reload
```
Ctrl+Shift+Delete → Clear cache → Reload page
```

### Fix 2: Force Logout and Re-login
1. Click user menu → Logout
2. Go to http://localhost:3000/login
3. Login again

### Fix 3: Restart Frontend Container
```bash
docker-compose restart frontend
```

### Fix 4: Check Keycloak Token Manually

In Browser Console:
```javascript
// Get Keycloak instance
const keycloak = JSON.parse(localStorage.getItem('keycloak'))

// Check token
console.log('Token:', keycloak?.token)

// Decode token (manual)
const tokenParts = keycloak?.token?.split('.')
if (tokenParts && tokenParts[1]) {
  const decoded = JSON.parse(atob(tokenParts[1]))
  console.log('Token payload:', decoded)
  console.log('Roles:', decoded.realm_access?.roles)
}
```

## Expected Debug Page Output (Administrator)

When logged in as administrator, debug page should show:

```
Authentication State
-------------------
Is Authenticated: true
Is Initialized: true
Current User: admin@greenschool.edu
Full Name: Admin User
Persona: administrator
Roles: administrator
User Role (computed): administrator
Has Token: Yes

Role Checks
-----------
Is Administrator: true
Is Teacher: false
Is Parent: false
Is Student: false
Can access users: true
Can access students: true
```

## Next Steps

1. **Login to the application**
2. **Navigate to: http://localhost:3000/debug**
3. **Take a screenshot of the debug page**
4. **Check browser console for errors**
5. **Report findings:**
   - What does "Is Authenticated" show?
   - What roles are listed?
   - Do role checks show true/false correctly?
   - Are there any console errors?

This information will help diagnose why navigation is not working after login.
