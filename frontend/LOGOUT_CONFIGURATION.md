# Logout URL Configuration

## Current Logout Configuration

The logout function is configured to redirect to:
```javascript
window.location.origin  // which equals: http://localhost:3000
```

## Keycloak Configuration Required

For logout to work properly, you need to configure **"Valid Post Logout Redirect URIs"** in Keycloak.

### Step 1: Access Keycloak Admin Console

1. Open: http://localhost:8080/admin
2. Login with admin credentials
3. Select realm: **green-school-id** (top-left dropdown)

### Step 2: Configure Post-Logout Redirect URIs

1. Navigate to: **Clients** (left sidebar)
2. Click on: **green-school-id**
3. Go to: **Settings** tab
4. Scroll down to find: **"Valid Post Logout Redirect URIs"**

### Step 3: Add Logout Redirect URIs

In the "Valid Post Logout Redirect URIs" field, add:

```
http://localhost:3000
http://localhost:3000/*
+
```

**Note:** The `+` symbol tells Keycloak to accept any URI that's in the "Valid Redirect URIs" list.

### Step 4: Verify Other Settings

While you're in the client settings, verify these are configured:

**Access Settings:**
- Root URL: `http://localhost:3000`
- Home URL: `http://localhost:3000`
- Valid Redirect URIs: `http://localhost:3000/*`
- Valid Post Logout Redirect URIs: `http://localhost:3000/*` or `+`
- Web Origins: `+` or `http://localhost:3000`

**Capability Config:**
- Client authentication: `OFF`
- Standard flow: `ON`
- Direct access grants: `ON`

### Step 5: Save and Test

1. Click **"Save"** at the bottom
2. Clear browser cache
3. Test logout:
   - Login to the app
   - Click user menu → Logout
   - Should redirect to http://localhost:3000

## Testing Logout

### With Enhanced Logging

I've added enhanced logging to the logout function. When you click logout, you'll see in console:

```
🚪 Logging out from Keycloak...
🚪 Logout redirect URI: http://localhost:3000
🚪 Current authenticated: true
```

### What Should Happen

1. User clicks "Logout" in app
2. Console shows logout messages
3. Browser redirects to Keycloak logout endpoint
4. Keycloak terminates session
5. Browser redirects back to: `http://localhost:3000`
6. App shows unauthenticated state (login page or home)

### What URL Keycloak Uses

When you logout, Keycloak redirects to:
```
http://localhost:8080/realms/green-school-id/protocol/openid-connect/logout?
  post_logout_redirect_uri=http://localhost:3000&
  id_token_hint=<token>
```

## Common Logout Issues

### Issue 1: "Invalid redirect uri" After Logout

**Error:** Keycloak shows error page saying "Invalid redirect uri"

**Cause:** `http://localhost:3000` is not in "Valid Post Logout Redirect URIs"

**Fix:** Add `http://localhost:3000/*` or `+` to "Valid Post Logout Redirect URIs" in Keycloak client settings.

### Issue 2: Logout Redirects to Wrong Page

**Symptom:** After logout, redirected to unexpected page

**Check:** The logout function uses `window.location.origin`

**If you want to redirect to a specific page after logout**, update the logout function:

```typescript
// Redirect to home page
keycloak.logout({
  redirectUri: window.location.origin + '/'
})

// Or redirect to login page
keycloak.logout({
  redirectUri: window.location.origin + '/login'
})
```

### Issue 3: User Still Authenticated After Logout

**Symptom:** Click logout, but user stays logged in

**Possible Causes:**
1. Logout function not being called
2. Keycloak logout failing silently
3. Local storage not being cleared

**Debug:**
- Check console for logout messages
- Check if localStorage is cleared: `localStorage.getItem('currentUser')`
- Check Network tab for logout request

### Issue 4: Session Persists in Keycloak

**Symptom:** After logout, going back to app auto-logs in again

**Cause:** Keycloak session still active

**This is expected behavior if:**
- You're testing in the same browser
- You have "Remember Me" enabled in Keycloak
- Session timeout hasn't occurred

**To fully test logout:**
1. Use incognito mode
2. Or manually logout from Keycloak:
   ```
   http://localhost:8080/realms/green-school-id/account
   ```
3. Or clear all cookies

## Updating Logout Redirect URI

If you want to change where logout redirects to:

### Option 1: Redirect to Login Page

**File:** `/frontend/src/services/keycloak.ts`

```typescript
export function logout(): void {
  const keycloak = getKeycloak()
  if (keycloak) {
    keycloak.logout({
      redirectUri: window.location.origin + '/login'  // 👈 Change here
    })
  }
}
```

### Option 2: Redirect to Home Page

```typescript
export function logout(): void {
  const keycloak = getKeycloak()
  if (keycloak) {
    keycloak.logout({
      redirectUri: window.location.origin + '/'  // 👈 Change here
    })
  }
}
```

### Option 3: Redirect to Current Page

```typescript
export function logout(): void {
  const keycloak = getKeycloak()
  if (keycloak) {
    keycloak.logout({
      redirectUri: window.location.href  // 👈 Stays on current page
    })
  }
}
```

**Remember:** Whatever URI you use must be in Keycloak's "Valid Post Logout Redirect URIs"

## Logout Flow Diagram

```
User clicks Logout
       ↓
App calls logout()
       ↓
Console logs logout info
       ↓
Keycloak.logout() called
       ↓
Browser redirects to Keycloak logout endpoint
       ↓
Keycloak terminates session
       ↓
Keycloak redirects to: post_logout_redirect_uri
       ↓
App receives redirect
       ↓
Auth state cleared (isAuthenticated = false)
       ↓
User sees login page or home page
```

## Verification Checklist

Test your logout configuration:

- [ ] Keycloak client has "Valid Post Logout Redirect URIs" configured
- [ ] Can login successfully
- [ ] User menu shows "Logout" option
- [ ] Clicking logout shows console messages
- [ ] Redirected to Keycloak logout endpoint
- [ ] Redirected back to app home page
- [ ] No longer authenticated (can't access protected routes)
- [ ] Login page or home page is shown
- [ ] localStorage is cleared
- [ ] No errors in console

## Test Logout Now

1. Restart frontend:
   ```bash
   docker-compose restart frontend
   ```

2. Login to the app

3. Open console (F12)

4. Click user menu → Logout

5. Watch console for:
   ```
   🚪 Logging out from Keycloak...
   🚪 Logout redirect URI: http://localhost:3000
   🚪 Current authenticated: true
   ```

6. Should redirect to http://localhost:3000 and show unauthenticated state

## Quick Fix Summary

**In Keycloak Admin Console:**

1. Clients → green-school-id → Settings
2. Add to "Valid Post Logout Redirect URIs":
   ```
   +
   ```
   Or:
   ```
   http://localhost:3000/*
   ```
3. Save
4. Test logout

That's it!
