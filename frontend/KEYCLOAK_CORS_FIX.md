# Fix Keycloak CORS Error

## Error Description
```
Access to XMLHttpRequest at 'http://localhost:8080/realms/green-school-id/protocol/openid-connect/token'
from origin 'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

This error occurs because Keycloak is not configured to accept requests from your frontend application running on `http://localhost:3000`.

## Solution: Configure Keycloak Client CORS Settings

### Step 1: Access Keycloak Admin Console

1. Open your browser and navigate to:
   ```
   http://localhost:8080/admin
   ```

2. Login with your admin credentials

3. Select the **`green-school-id`** realm from the realm dropdown (top-left corner)

### Step 2: Configure Client Settings

1. In the left sidebar, click **"Clients"**

2. Find and click on **`green-school-id`** client in the list

3. Go to the **"Settings"** tab

### Step 3: Update CORS Configuration

Scroll down to find these settings and configure them as follows:

#### **Valid Redirect URIs**
Add these URLs (one per line):
```
http://localhost:3000/*
http://localhost:3000/dashboard
http://localhost:3000/login
```

#### **Valid Post Logout Redirect URIs**
Add:
```
http://localhost:3000/*
```

#### **Web Origins**
Add ONE of these options:

**Option A: Wildcard (Recommended for Development)**
```
+
```
The `+` symbol tells Keycloak to automatically allow CORS from all URLs listed in "Valid Redirect URIs"

**Option B: Explicit Origins**
```
http://localhost:3000
```

#### **Root URL**
```
http://localhost:3000
```

#### **Home URL**
```
http://localhost:3000
```

### Step 4: Additional Client Settings

Make sure these are configured:

#### **Access Settings**
- **Client authentication**: `OFF` (public client)
- **Authorization**: `OFF`
- **Authentication flow**:
  - ✅ **Standard flow**: ON
  - ✅ **Direct access grants**: ON
  - ❌ **Implicit flow**: OFF
  - ❌ **Service accounts roles**: OFF

#### **Login Settings**
- **Consent required**: OFF
- **Display client on consent screen**: OFF

### Step 5: Save Changes

1. Scroll to the bottom
2. Click **"Save"** button
3. Wait for the success message

### Step 6: Test the Configuration

1. Clear your browser cache:
   - Chrome/Edge: `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Click "Clear data"

2. Close all browser tabs for `localhost:3000`

3. Open a new tab and navigate to:
   ```
   http://localhost:3000
   ```

4. Open Developer Tools (F12) → Console tab

5. Click "Sign In"

6. The CORS error should be gone!

## Visual Guide for Keycloak Configuration

### Client Settings Location
```
Keycloak Admin Console
  └─ Select Realm: "green-school-id"
      └─ Clients (left sidebar)
          └─ Click "green-school-id"
              └─ Settings tab
                  ├─ Root URL: http://localhost:3000
                  ├─ Home URL: http://localhost:3000
                  ├─ Valid Redirect URIs: http://localhost:3000/*
                  ├─ Valid Post Logout Redirect URIs: http://localhost:3000/*
                  └─ Web Origins: +
```

### Important Notes

**About "Web Origins: +"**
- The `+` symbol is a special value in Keycloak
- It means: "Allow CORS from any URL that's in Valid Redirect URIs"
- This is the easiest and most flexible option for development

**About "Web Origins: http://localhost:3000"**
- This explicitly allows only `http://localhost:3000`
- More secure but less flexible
- You'd need to add each origin manually

## Verification Steps

### 1. Check Keycloak Configuration
After saving, verify the settings:

1. Go back to Clients → green-school-id → Settings
2. Scroll down to verify:
   - Web Origins shows `+` or `http://localhost:3000`
   - Valid Redirect URIs contains `http://localhost:3000/*`
   - Client authentication is OFF

### 2. Test CORS with Browser Console

Open Developer Tools and run this in the console:

```javascript
fetch('http://localhost:8080/realms/green-school-id/.well-known/openid-configuration')
  .then(r => r.json())
  .then(data => console.log('✅ CORS working!', data))
  .catch(err => console.error('❌ CORS error:', err))
```

If CORS is working, you'll see the configuration object.

### 3. Test Authentication Flow

1. Go to http://localhost:3000
2. Click "Sign In"
3. Enter credentials: `admin@greenschool.edu` / `Admin123`
4. Check console - you should see:
   ```
   🔐 Initializing Keycloak authentication...
   🔄 Initializing Keycloak...
   User is authenticated
   👤 User profile loaded: admin@greenschool.edu administrator
   ✅ Keycloak authentication successful: Admin User (administrator)
   ```

No CORS errors!

## Alternative: Keycloak CLI Configuration

If you prefer using the command line, you can configure CORS with the Keycloak Admin CLI:

```bash
# Login to Keycloak CLI
/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 \
  --realm master \
  --user admin

# Update client CORS settings
/opt/keycloak/bin/kcadm.sh update clients/<client-uuid> \
  -r green-school-id \
  -s 'webOrigins=["http://localhost:3000"]' \
  -s 'redirectUris=["http://localhost:3000/*"]'
```

## Common Issues

### Issue: "Still getting CORS error after configuration"

**Solutions:**
1. Hard refresh the browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache completely
3. Try in incognito/private browsing mode
4. Restart Keycloak server
5. Verify you saved the settings in Keycloak

### Issue: "Configuration looks correct but still not working"

**Check:**
1. Did you select the correct realm? (green-school-id)
2. Did you edit the correct client? (green-school-id)
3. Did you click "Save" after making changes?
4. Try using `+` instead of explicit origin
5. Check Keycloak logs for errors:
   ```bash
   docker logs keycloak-container-name
   ```

### Issue: "Getting other errors after fixing CORS"

**Next steps:**
1. Check that user exists in Keycloak
2. Verify user has assigned roles
3. Check user email is verified
4. Ensure password is set correctly (not temporary)

## For Production

When deploying to production, replace localhost URLs with your actual domain:

```
Root URL: https://yourdomain.com
Home URL: https://yourdomain.com
Valid Redirect URIs: https://yourdomain.com/*
Valid Post Logout Redirect URIs: https://yourdomain.com/*
Web Origins: https://yourdomain.com
```

Or use `+` in Web Origins to automatically allow all redirect URIs.

## Quick Checklist

Before testing, verify these are configured in Keycloak:

- [ ] Realm: `green-school-id` is selected
- [ ] Client: `green-school-id` exists
- [ ] Root URL: `http://localhost:3000`
- [ ] Home URL: `http://localhost:3000`
- [ ] Valid Redirect URIs: `http://localhost:3000/*`
- [ ] Web Origins: `+` or `http://localhost:3000`
- [ ] Client Authentication: OFF
- [ ] Standard Flow: ON
- [ ] Settings are saved
- [ ] Browser cache is cleared

## Need Help?

If you're still having issues:

1. Export your client configuration:
   - In Keycloak Admin Console
   - Clients → green-school-id → Action → Export
   - Check the JSON for CORS settings

2. Check Keycloak server logs for errors

3. Test with curl to verify Keycloak is accessible:
   ```bash
   curl -v http://localhost:8080/realms/green-school-id/.well-known/openid-configuration
   ```

4. Verify Keycloak is running:
   ```bash
   curl http://localhost:8080
   ```
