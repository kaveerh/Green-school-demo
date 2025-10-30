# Keycloak Configuration Guide

This guide explains how to configure Keycloak for the Green School Management System frontend.

## Prerequisites

- Keycloak running at http://localhost:8080
- Admin access to Keycloak
- Realm: `green-school-id`
- Client: `green-school-id`

## Configuration Steps

### 1. Access Keycloak Admin Console

1. Navigate to http://localhost:8080/admin
2. Login with your admin credentials
3. Select the `green-school-id` realm from the dropdown

### 2. Configure the Client

Navigate to **Clients** → **green-school-id** and configure the following:

#### General Settings
- **Client ID**: `green-school-id`
- **Name**: Green School Management System
- **Enabled**: ON

#### Access Settings
- **Root URL**: `http://localhost:3000`
- **Home URL**: `http://localhost:3000`
- **Valid Redirect URIs**:
  - `http://localhost:3000/*`
  - `http://localhost:3000/silent-check-sso.html`
- **Valid Post Logout Redirect URIs**: `http://localhost:3000/*`
- **Web Origins**: `http://localhost:3000`

#### Capability Config
- **Client authentication**: OFF (for public clients)
- **Authorization**: OFF
- **Authentication flow**:
  - ✅ Standard flow
  - ✅ Direct access grants
  - ❌ Implicit flow
  - ❌ Service accounts roles

#### Login Settings
- **Login theme**: keycloak (or your custom theme)
- **Consent required**: OFF
- **Display client on consent screen**: OFF

### 3. Configure CORS

Under **Advanced Settings**:
- **Web Origins**: `+` (or explicitly `http://localhost:3000`)

### 4. Create Test Users

Navigate to **Users** → **Add User**:

#### Administrator User
- **Username**: admin@greenschool.edu
- **Email**: admin@greenschool.edu
- **First Name**: Admin
- **Last Name**: User
- **Email Verified**: ON
- **Credentials** Tab:
  - Password: Admin123
  - Temporary: OFF
- **Role Mappings** Tab:
  - Assign realm role: `administrator`

#### Teacher User
- **Username**: teacher@greenschool.edu
- **Email**: teacher@greenschool.edu
- **First Name**: Teacher
- **Last Name**: User
- **Email Verified**: ON
- **Credentials** Tab:
  - Password: Admin123
  - Temporary: OFF
- **Role Mappings** Tab:
  - Assign realm role: `teacher`

#### Parent User
- **Username**: parent@greenschool.edu
- **Email**: parent@greenschool.edu
- **First Name**: Parent
- **Last Name**: User
- **Email Verified**: ON
- **Credentials** Tab:
  - Password: Admin123
  - Temporary: OFF
- **Role Mappings** Tab:
  - Assign realm role: `parent`

#### Student User
- **Username**: student@greenschool.edu
- **Email**: student@greenschool.edu
- **First Name**: Student
- **Last Name**: User
- **Email Verified**: ON
- **Credentials** Tab:
  - Password: Admin123
  - Temporary: OFF
- **Role Mappings** Tab:
  - Assign realm role: `student`

### 5. Configure Realm Roles

Navigate to **Realm Roles** and ensure these roles exist:
- `administrator`
- `teacher`
- `parent`
- `student`
- `vendor`

### 6. Token Settings (Optional)

Under **Realm Settings** → **Tokens**:
- **Access Token Lifespan**: 5 minutes (default)
- **SSO Session Idle**: 30 minutes
- **SSO Session Max**: 10 hours
- **Refresh Token Max Reuse**: 0

### 7. Content Security Policy (CSP)

If you still encounter CSP issues:

1. Navigate to **Realm Settings** → **Security Defenses**
2. Update **Content-Security-Policy**:
   ```
   frame-src 'self' http://localhost:3000; frame-ancestors 'self' http://localhost:3000; object-src 'none';
   ```

### 8. Test Configuration

1. Go to http://localhost:3000
2. Click "Sign In"
3. Enter credentials (e.g., admin@greenschool.edu / Admin123)
4. Verify successful login and redirect to dashboard

## Troubleshooting

### Error: "Invalid redirect_uri"
- Check that `http://localhost:3000/*` is in Valid Redirect URIs
- Ensure there are no trailing spaces

### Error: "CORS error"
- Check Web Origins is set to `http://localhost:3000` or `+`
- Verify client is enabled

### Error: "frame-ancestors CSP violation"
- Update CSP settings in Realm Settings → Security Defenses
- Or disable silent SSO check in frontend (already done)

### Error: "User not found"
- Verify user exists in Keycloak
- Check email is verified
- Ensure user has correct realm roles assigned

## Quick Setup Script

Here's a quick test to verify Keycloak is accessible:

```bash
# Test Keycloak is running
curl http://localhost:8080/realms/green-school-id/.well-known/openid-configuration

# Should return JSON with configuration details
```

## Environment Variables

Ensure your `.env` file has:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=green-school-id
VITE_KEYCLOAK_CLIENT_ID=green-school-id
```

## Next Steps

After configuration:
1. Restart frontend container: `docker-compose restart frontend`
2. Clear browser cache
3. Test login flow at http://localhost:3000/login
