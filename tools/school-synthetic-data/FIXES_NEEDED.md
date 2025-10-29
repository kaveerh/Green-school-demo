# API Alignment Fixes Needed

## ✅ Working Features
1. Schools - Using existing school
2. Users (all personas) - Fixed phone number format
3. Students - Fixed allergies format and status enum
4. Attendance - Working

## ❌ Features Needing Fixes

### 1. Teachers
- Error: 400 Bad Request
- Need to check API schema

### 2. Parents  
- Error: 422 Unprocessable Entity
- Need to check required fields

### 3. Subjects
- Error: 400 Bad Request
- Codes must use underscores only (no hyphens) - ALREADY FIXED IN CONFIG

### 4. Rooms
- Error: 400 Bad Request
- Need to check API schema

### 5. Events
- Error: `created_by_id` required as query parameter
- Should be in request body, not query

### 6. Vendors
- Error: `created_by_id` required as query parameter
- Should be in request body, not query

### 7. Activities
- Depends on teachers (which failed)

### 8. Merits
- Depends on teachers (which failed)

### 9. Classes
- Depends on subjects (which failed)

### 10. Lessons
- Depends on classes (which failed)

## Next Steps
1. Fix Teachers API call
2. Fix Parents API call
3. Fix Subjects API call (check if config codes are correct)
4. Fix Rooms API call
5. Fix Events - add created_by_id to body
6. Fix Vendors - add created_by_id to body
