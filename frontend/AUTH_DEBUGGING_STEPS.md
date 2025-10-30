# Authentication Debugging Steps

## The Problem

You're seeing: `Navigating to: /login, Requires Auth: false, Is Authenticated: false`

This means the login is **NOT completing successfully**. The user is not being authenticated after the Keycloak redirect.

## Enhanced Logging Now Active

I've added detailed logging to track exactly what's happening during the authentication process.

## Step-by-Step Debug Process

### Step 1: Clear Everything

**Clear browser cache completely:**
- Chrome/Edge: `Ctrl+Shift+Delete` → Select "All time" → Check "Cached images and files" → Clear
- Or use Incognito mode for a clean test

### Step 2: Open Console BEFORE Logging In

1. Open http://localhost:3000
2. **BEFORE clicking anything**, open DevTools (F12)
3. Go to **Console** tab
4. Keep console open throughout the entire process

### Step 3: Start Login Process

1. Click "Sign In" or go to http://localhost:3000/login
2. **WATCH THE CONSOLE** - you should see:
   ```
   🔐 Initializing Keycloak authentication...
   🔄 Initializing Keycloak...
   🔑 Keycloak.init() starting...
   🔑 Current URL: http://localhost:3000/...
   ```

3. Click "Sign In with Keycloak" button
4. **WATCH THE CONSOLE** - you should see:
   ```
   🔐 Initiating Keycloak login...
   🔐 Redirect URI: http://localhost:3000/dashboard
   ```

### Step 4: Complete Keycloak Login

1. You'll be redirected to Keycloak login page
2. Enter credentials: `admin@greenschool.edu` / `Admin123`
3. Click login on Keycloak page

### Step 5: Watch the Redirect Back

**CRITICAL: After logging in at Keycloak, you'll be redirected back to your app**

Watch the console carefully. You should see:

```
🔑 Keycloak.init() starting...
🔑 Current URL: http://localhost:3000/dashboard?...
🔑 Keycloak.init() completed
🔑 Authenticated: true or false <-- THIS IS KEY
🔑 Token present: true or false
🔑 Token parsed: true or false
```

**If Authenticated: true**
```
✅ User is authenticated
✅ Token: eyJhbGciOiJSUzI1NiIsInR5cCI...
✅ Token parsed: { ... user data ... }
👤 User profile loaded: admin@greenschool.edu administrator
✅ Keycloak authentication successful: Admin User (administrator)
```

**If Authenticated: false**
```
❌ User is not authenticated
❌ Keycloak object: { authenticated: false, token: 'missing', tokenParsed: 'missing' }
```

### Step 6: Copy ALL Console Output

1. Right-click in console
2. Select "Save as..."
3. Or copy all text
4. Share the output with me

## What to Look For

### Scenario A: Token Not Being Received

**Console shows:**
```
🔑 Authenticated: false
🔑 Token present: false
🔑 Token parsed: false
```

**This means:** Keycloak redirected back but didn't provide a token.

**Possible causes:**
1. Keycloak redirect URI mismatch
2. CORS blocking the token exchange
3. Keycloak client configuration issue

### Scenario B: Token Received But Not Parsed

**Console shows:**
```
🔑 Authenticated: true
🔑 Token present: true
🔑 Token parsed: false
```

**This means:** Token was received but couldn't be decoded.

**Possible causes:**
1. Invalid JWT format
2. Token encryption issue
3. Missing claims in token

### Scenario C: Keycloak Init Failed

**Console shows:**
```
❌ Failed to initialize Keycloak: [error message]
❌ Error details: { ... }
```

**This means:** Keycloak.init() threw an error.

**Possible causes:**
1. Keycloak server not accessible
2. Invalid Keycloak configuration
3. Network error

### Scenario D: URL Parameters Missing

**After redirect, check the URL:**

**Expected:**
```
http://localhost:3000/dashboard?state=...&session_state=...&code=...
```

**If you don't see `code=` in the URL:** Keycloak didn't provide an authorization code.

**Possible causes:**
1. Keycloak client not configured for authorization code flow
2. Standard flow not enabled in Keycloak
3. Redirect URI mismatch

## Quick Checks

### Check 1: Verify Keycloak is Accessible

Open in browser:
```
http://localhost:8080/realms/green-school-id/.well-known/openid-configuration
```

Should return JSON configuration.

### Check 2: Verify Redirect URI in Keycloak

1. Go to: http://localhost:8080/admin
2. Login as admin
3. Select realm: green-school-id
4. Clients → green-school-id → Settings
5. **Check "Valid Redirect URIs":**
   - Must include: `http://localhost:3000/*`
   - Or specifically: `http://localhost:3000/dashboard*`

### Check 3: Verify Standard Flow Enabled

In Keycloak client settings:
- **Standard flow**: Must be ON
- **Direct access grants**: Should be ON
- **Client authentication**: Should be OFF (public client)

### Check 4: Verify Web Origins

In Keycloak client settings:
- **Web Origins**: Should be `+` or `http://localhost:3000`

## Common Issues

### Issue 1: "Invalid redirect_uri"

**Error in console or Keycloak:**
```
Invalid parameter: redirect_uri
```

**Fix:**
Add `http://localhost:3000/*` to "Valid Redirect URIs" in Keycloak client settings.

### Issue 2: CORS Error During Token Exchange

**Error in console:**
```
Access to XMLHttpRequest at 'http://localhost:8080/realms/.../token' blocked by CORS
```

**Fix:**
Set "Web Origins" to `+` in Keycloak client settings.

### Issue 3: User Redirected to Login Again

**What happens:**
- Login at Keycloak succeeds
- Redirected back to app
- Immediately redirected back to /login

**This means:** Token wasn't stored or authentication state not set.

**Check console for:**
- Token present: false
- Authenticated: false

### Issue 4: Blank Page After Redirect

**What happens:**
- Login at Keycloak succeeds
- Redirected back to app
- Page loads but shows nothing

**Check console for:**
- JavaScript errors
- Component loading errors
- Router errors

## Test Without Login (Direct Token Check)

If you want to test if an existing session works:

1. Login to Keycloak directly:
   ```
   http://localhost:8080/realms/green-school-id/account
   ```

2. Login with test credentials

3. Go back to your app:
   ```
   http://localhost:3000
   ```

4. Keycloak should detect existing session and authenticate automatically

## Expected Full Console Output

Here's what you should see for a **successful** login:

```
🔐 Initializing Keycloak authentication...
🔄 Initializing Keycloak...
🔑 Keycloak.init() starting...
🔑 Current URL: http://localhost:3000/
🔑 Keycloak.init() completed
🔑 Authenticated: false
🔑 Token present: false
🔑 Token parsed: false
❌ User is not authenticated
❌ Keycloak object: {authenticated: false, token: "missing", tokenParsed: "missing"}
ℹ️ User is not authenticated
✓ Auth initialization complete. Authenticated: false

[User clicks Sign In]

🔐 Initiating Keycloak login...
🔐 Redirect URI: http://localhost:3000/dashboard

[Redirected to Keycloak, user enters credentials]

[Redirected back to app]

🔐 Initializing Keycloak authentication...
🔄 Initializing Keycloak...
🔑 Keycloak.init() starting...
🔑 Current URL: http://localhost:3000/dashboard?state=abc123&session_state=xyz789&code=def456
🔑 Keycloak.init() completed
🔑 Authenticated: true
🔑 Token present: true
🔑 Token parsed: true
✅ User is authenticated
✅ Token: eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6...
✅ Token parsed: {exp: 1234567890, iat: 1234567890, auth_time: 1234567890, ...}
👤 User profile loaded: admin@greenschool.edu administrator
✅ Keycloak authentication successful: Admin User (administrator)
🏫 Available schools: 1
✓ Auth initialization complete. Authenticated: true
🧭 Navigating to: /dashboard, Requires Auth: true, Is Authenticated: true
```

## What to Share

After following these steps, share:

1. **Full console output** (copy and paste all of it)
2. **What URL you see** after redirect (including query parameters)
3. **Whether you see any error messages** in console
4. **Screenshot of Keycloak client settings** (Valid Redirect URIs and Web Origins)

This detailed logging will help us identify exactly where the authentication is failing.
