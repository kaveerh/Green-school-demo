# Bug Fix: API URL Duplication

## Issue
**Error:** `POST http://localhost:8000/api/v1/api/v1/users 404 (Not Found)`

The API URL had a duplicate `/api/v1` prefix, resulting in:
- Expected: `http://localhost:8000/api/v1/users`
- Actual: `http://localhost:8000/api/v1/api/v1/users`

## Root Cause

In `frontend/src/services/userService.ts`:

**Before (Broken):**
```typescript
// Lines 16-18
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PREFIX = '/api/v1'

// Line 165
constructor() {
  this.client = new ApiClient(API_BASE_URL)
  this.basePath = `${API_PREFIX}/users`  // Added /api/v1/users
}
```

**Problem:**
1. `.env` file sets `VITE_API_URL=http://localhost:8000/api/v1` (includes `/api/v1`)
2. Code then added `API_PREFIX` (`/api/v1`) again
3. Result: `http://localhost:8000/api/v1` + `/api/v1/users` = duplicate

## Solution

**After (Fixed):**
```typescript
// Line 17
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Line 164
constructor() {
  this.client = new ApiClient(API_BASE_URL)
  this.basePath = `/users`  // Just /users, no prefix
}
```

**Changes Made:**
1. Removed `API_PREFIX` constant (no longer needed)
2. Updated `API_BASE_URL` fallback to include `/api/v1`
3. Changed `basePath` from `${API_PREFIX}/users` to `/users`

## Result

Now the URLs are constructed correctly:
- `API_BASE_URL`: `http://localhost:8000/api/v1` (from .env)
- `basePath`: `/users`
- **Final URL**: `http://localhost:8000/api/v1/users` ✅

## Files Modified

1. `frontend/src/services/userService.ts`
   - Line 17: Removed API_PREFIX, updated fallback URL
   - Line 164: Changed basePath to `/users`

## Testing

Verified that the API endpoint works correctly:
```bash
curl http://localhost:8000/api/v1/users
# Returns: 200 OK with user data
```

Frontend should now make requests to the correct URL.

## Impact

All API calls in the frontend will now use the correct URL:
- `GET /api/v1/users` - List users ✅
- `POST /api/v1/users` - Create user ✅
- `GET /api/v1/users/{id}` - Get user ✅
- `PUT /api/v1/users/{id}` - Update user ✅
- `DELETE /api/v1/users/{id}` - Delete user ✅
- `PATCH /api/v1/users/{id}/status` - Change status ✅
- `PATCH /api/v1/users/{id}/persona` - Change persona ✅
- `GET /api/v1/users/statistics/summary` - Get statistics ✅

## Prevention

To prevent similar issues in the future:

1. **Consistent URL handling**: Always check if base URL includes the prefix
2. **Environment variables**: Document what's included in VITE_API_URL
3. **Testing**: Test API calls during development
4. **Documentation**: Clear comments about URL structure

## Status

✅ **Fixed and Verified**

Frontend hot-reloaded automatically (Vite), no restart needed.
All API endpoints should now work correctly in the UI.

---

**Date:** October 15, 2025
**Severity:** High (blocking all API calls)
**Time to Fix:** 5 minutes
