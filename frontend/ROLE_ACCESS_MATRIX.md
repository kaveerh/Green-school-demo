# Role-Based Access Control Matrix

## Overview

This document describes what features each user role (persona) can access in the Green School Management System.

## Access by Role

### 👨‍💼 Administrator
**Full System Access** - Can manage everything

**Navigation Menu Items:**
- ✅ Dashboard
- ✅ Users (create, edit, delete)
- ✅ Schools (create, edit, delete)
- ✅ Teachers (manage)
- ✅ Students (manage)
- ✅ Parents (manage)
- ✅ Subjects (manage)
- ✅ Rooms (manage)
- ✅ Classes (manage)
- ✅ Lessons (view, manage)
- ✅ Assessments (create, grade, view)
- ✅ Attendance (mark, view)
- ✅ Events (create, edit, delete)
- ✅ Activities (create, manage roster)
- ✅ Vendors (manage)
- ✅ Merits (award, view leaderboard)

**Permissions:**
- Full CRUD operations on all entities
- Can assign roles to users
- Can configure school settings
- Can view all reports and statistics

---

### 👨‍🏫 Teacher
**Classroom Management** - Focused on teaching activities

**Navigation Menu Items:**
- ✅ Dashboard
- ✅ Students (view, limited editing)
- ✅ Parents (view, communicate)
- ✅ Subjects (view)
- ✅ Rooms (view)
- ✅ Classes (view their assigned classes)
- ✅ Lessons (create, edit for their classes)
- ✅ Assessments (create, grade for their classes)
- ✅ Attendance (mark for their classes)
- ✅ Events (view, create)
- ✅ Activities (view, manage assigned activities)
- ✅ Merits (award to their students)

**Permissions:**
- Can create and grade assessments for their classes
- Can mark attendance for their classes
- Can create lesson plans
- Can view and contact parents
- Can award merit points to students
- Cannot modify system settings
- Cannot manage users or schools

---

### 🎓 Student (UPDATED)
**Personal Academic View** - View own academic information

**Navigation Menu Items:**
- ✅ Dashboard (personal overview)
- ✅ Classes (view schedule and class information)
- ✅ Assessments (view own grades and feedback)
- ✅ Attendance (view own attendance records)
- ✅ Events (view school events)
- ✅ Activities (view and join activities)
- ✅ Merits (view own merit points and leaderboard)

**Permissions:**
- **Read-only access** to own academic data
- Can view own grades and assessment feedback
- Can view own attendance records
- Can view class schedule
- Can view school events and activities
- Can view merit points earned
- Cannot edit or create any data
- Cannot view other students' information

**What Students See:**
- Personal dashboard with GPA, attendance summary
- List of enrolled classes with schedules
- Grades and feedback on assessments
- Attendance history
- Upcoming school events
- Available extracurricular activities
- Merit points earned and class ranking

---

### 👪 Parent (UPDATED)
**Child Monitoring** - Monitor children's academic progress

**Navigation Menu Items:**
- ✅ Dashboard (children overview)
- ✅ Classes (view children's schedules)
- ✅ Assessments (view children's grades)
- ✅ Attendance (view children's attendance)
- ✅ Events (view school events)
- ✅ Activities (view children's activities)
- ✅ Merits (view children's merit points)

**Permissions:**
- **Read-only access** to their children's academic data
- Can view children's grades and assessment feedback
- Can view children's attendance records
- Can view children's class schedules
- Can view school events
- Can view children's extracurricular activities
- Can view children's merit points
- Cannot edit or create any data
- Cannot view other students' information (except their own children)

**What Parents See:**
- Dashboard showing all their children's progress
- Each child's class schedule
- Grades and teacher feedback for each child
- Attendance records for each child
- School calendar with events
- Children's activity participation
- Merit points and achievements per child

---

### 🏢 Vendor (Not Changed)
**Limited External Access** - Event-related viewing only

**Navigation Menu Items:**
- ✅ Dashboard
- ❌ Limited access to other features

**Permissions:**
- Can view event attendance (for catering/supplies)
- Can view supply orders
- Can communicate with administrators
- Very restricted access

---

## Access Control Implementation

### How It Works

**Navigation Component:** `/frontend/src/components/AppNavigation.vue`

Each menu item has a computed property that checks if the current user has the required role(s):

```typescript
// Example: Students and parents can view assessments
const canAccessAssessments = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher', 'student', 'parent'])
})
```

**Router Guards:** `/frontend/src/router/index.ts`

Each route has metadata specifying required roles:

```typescript
{
  path: '/assessments',
  meta: {
    requiresAuth: true,
    requiresRole: ['administrator', 'teacher', 'student', 'parent']
  }
}
```

### Role Checking Functions

**In Auth Store:** `/frontend/src/stores/authStore.ts`

```typescript
// Check if user has a specific role
hasRole(role: string): boolean

// Check if user has any of the specified roles
hasAnyRole(roles: string[]): boolean
```

These functions check both:
1. Keycloak realm roles (from JWT token)
2. User persona field (from database)

## Feature-Level Permissions

Beyond just viewing, the actual components implement feature-level restrictions:

### Students Can:
- ✅ View own assessments (grades)
- ✅ View own attendance
- ✅ View class schedule
- ✅ View school events
- ✅ View merit points
- ❌ Cannot edit anything
- ❌ Cannot create assessments
- ❌ Cannot mark attendance
- ❌ Cannot view other students' data

### Parents Can:
- ✅ View children's assessments
- ✅ View children's attendance
- ✅ View children's schedule
- ✅ View school events
- ✅ View children's activities
- ❌ Cannot edit anything
- ❌ Cannot create assessments
- ❌ Cannot mark attendance
- ❌ Cannot view other students' data

### Teachers Can:
- ✅ Create and grade assessments for their classes
- ✅ Mark attendance for their classes
- ✅ Create lesson plans
- ✅ View and contact parents
- ✅ Award merit points
- ❌ Cannot manage users or schools
- ❌ Cannot access admin settings
- ❌ Cannot view classes they don't teach

## Testing Access by Role

### Test as Student

1. Login as: `student@greenschool.edu` / `Admin123`
2. **Should see in navigation:**
   - Dashboard
   - Classes
   - Assessments
   - Attendance
   - Events
   - Activities
   - Merits
3. **Should NOT see:**
   - Users, Schools, Teachers, Students, Parents
   - Subjects, Rooms, Lessons
   - Vendors

### Test as Parent

1. Login as: `parent@greenschool.edu` / `Admin123`
2. **Should see in navigation:**
   - Dashboard
   - Classes (children's schedules)
   - Assessments (children's grades)
   - Attendance (children's records)
   - Events
   - Activities (children's activities)
   - Merits (children's points)
3. **Should NOT see:**
   - Users, Schools, Teachers, Students, Parents
   - Subjects, Rooms, Lessons
   - Vendors

### Test as Teacher

1. Login as: `teacher@greenschool.edu` / `Admin123`
2. **Should see in navigation:**
   - All except: Users, Schools, Teachers, Vendors
3. **Should be able to:**
   - Create assessments
   - Mark attendance
   - Create lessons
   - Award merits

### Test as Administrator

1. Login as: `admin@greenschool.edu` / `Admin123`
2. **Should see in navigation:**
   - Everything (all menu items)
3. **Should be able to:**
   - Full CRUD on all features

## Updating Role Access

### To Grant Access to a Feature

Edit: `/frontend/src/components/AppNavigation.vue`

Find the computed property for that feature and add the role:

```typescript
// Before: Only admin and teacher
const canAccessAssessments = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

// After: Add student and parent
const canAccessAssessments = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher', 'student', 'parent'])
})
```

### To Update Route Protection

Edit: `/frontend/src/router/index.ts`

Update the route's meta.requiresRole:

```typescript
{
  path: '/assessments',
  name: 'assessments',
  component: () => import('@/views/AssessmentList.vue'),
  meta: {
    requiresAuth: true,
    requiresRole: ['administrator', 'teacher', 'student', 'parent'] // Add roles here
  }
}
```

## Summary of Changes Made

**Updated Access for Students and Parents:**

Previously, students and parents could only access:
- ❌ Dashboard only

Now, students and parents can access:
- ✅ Dashboard
- ✅ Classes (view schedule)
- ✅ Assessments (view grades)
- ✅ Attendance (view records)
- ✅ Events (view school events)
- ✅ Activities (view activities)
- ✅ Merits (view points)

**Files Modified:**
- `/frontend/src/components/AppNavigation.vue` (role checks updated)

**Restart Required:**
- Frontend has been restarted with new access rules

## Verification

After login as student or parent, you should now see 7 menu items in the sidebar:
1. 🏠 Dashboard
2. 📚 Classes
3. 📝 Assessments
4. 📅 Attendance
5. 🎉 Events
6. 🎭 Activities
7. ⭐ Merits

These provide read-only access to view personal/children's academic information.
