# Green School Management System - Frontend Documentation

**Version:** 1.0.0
**Last Updated:** October 31, 2025
**Author:** Auto-generated documentation

---

## Table of Contents

1. [Introduction](#introduction)
2. [User Roles](#user-roles)
3. [Feature Documentation](#feature-documentation)
   - [1. Users](#1-users)
   - [2. Schools](#2-schools)
   - [3. Teachers](#3-teachers)
   - [4. Students](#4-students)
   - [5. Parents](#5-parents)
   - [6. Subjects](#6-subjects)
   - [7. Rooms](#7-rooms)
   - [8. Classes](#8-classes)
   - [9. Lessons](#9-lessons)
   - [10. Assessments](#10-assessments)
   - [11. Attendance](#11-attendance)
   - [12. Events](#12-events)
   - [13. Activities](#13-activities)
   - [14. Vendors](#14-vendors)
   - [15. Merits](#15-merits)
4. [Role-Based Access Control Matrix](#role-based-access-control-matrix)

---

## Introduction

This document provides comprehensive frontend documentation for the Green School Management System. It covers all 15 core features, detailing form fields, field types, validation rules, placeholder text, and user role permissions.

### System Overview

- **Frontend Framework:** Vue 3 + TypeScript + Vite
- **State Management:** Pinia
- **Styling:** Tailwind CSS
- **Authentication:** Keycloak SSO
- **Base URL:** http://localhost:3000
- **Backend API:** http://localhost:8000

### Documentation Scope

For each feature, this document includes:
- Feature description
- List and detail views
- Create/edit forms with complete field specifications
- User role permissions (View, Create, Edit, Delete)
- Form validation rules
- Placeholder text and help text

---

## User Roles

The system supports five distinct user roles, each with specific permissions:

1. **Administrator** - Full system access, user management, school configuration
2. **Teacher** - Manage classes, lessons, assessments, attendance
3. **Student** - View personal classes, grades, attendance
4. **Parent** - View children's progress, grades, attendance
5. **Vendor** - Limited access to vendor-specific features

---

## Feature Documentation

---

## 1. Users

### Overview
User management is the foundation feature that handles all system users across different personas (roles). Administrators can create, edit, and manage users for all roles.

### Views
- **List View:** `/users` - Displays paginated table of all users with filtering
- **Detail View:** `/users/:id` - Shows complete user profile
- **Create View:** `/users/create` - Form to create new user
- **Edit View:** `/users/:id/edit` - Form to edit existing user

### List View Features
- **Search:** Filter by name or email
- **Filters:**
  - Persona dropdown (All, Administrator, Teacher, Student, Parent, Vendor)
  - Status dropdown (All, Active, Inactive, Suspended)
- **Pagination:** 20 users per page
- **Actions:** View, Edit, Delete buttons per user
- **Display Columns:** Name (with avatar), Email, Persona (badge), Status (badge), Created Date

### Create/Edit Form

#### Form Sections

##### Personal Information
| Field | Type | Required | Placeholder | Validation | Notes |
|-------|------|----------|-------------|------------|-------|
| First Name | text | Yes | Enter first name | - | - |
| Last Name | text | Yes | Enter last name | - | - |
| Email | email | Yes | user@example.com | Valid email format | Cannot be changed in edit mode |
| Phone | tel | No | +1234567890 | - | - |

##### Account Settings
| Field | Type | Required | Placeholder | Options/Help | Notes |
|-------|------|----------|-------------|--------------|-------|
| Persona (Role) | select | Yes | Select persona | Administrator, Teacher, Student, Parent, Vendor | Determines user permissions and access |
| School ID | text | Yes | Enter school UUID | - | UUID of the school this user belongs to. Only shown in create mode |
| Password | password | Yes | Enter password | - | Must be at least 8 characters with uppercase, digit, and special character. Only shown in create mode |

##### Additional Information
| Field | Type | Required | Placeholder | Notes |
|-------|------|----------|-------------|-------|
| Avatar URL | url | No | https://example.com/avatar.jpg | - |
| Bio | textarea | No | Enter a brief bio | 4 rows |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Detail | ✅ | Own profile only | Own profile only | Own profile only | Own profile only |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | Own profile only | Own profile only | Own profile only | Own profile only |
| Delete | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 2. Schools

### Overview
School management feature for multi-tenant configuration. Each school is a separate tenant with isolated data.

### Views
- **List View:** `/schools` - Grid/table of all schools
- **Detail View:** `/schools/:id` - School profile with stats
- **Create View:** `/schools/create` - New school registration form
- **Edit View:** `/schools/:id/edit` - School information editor

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder | Validation | Help Text |
|-------|------|----------|-------------|------------|-----------|
| School Name | text | Yes | Enter school name | - | - |
| URL Slug | text | No | url-friendly-name (auto-generated if empty) | Pattern: [a-z0-9\-]+ | URL-friendly identifier (lowercase, numbers, hyphens only) |

##### Address
| Field | Type | Required | Placeholder | Default |
|-------|------|----------|-------------|---------|
| Address Line 1 | text | No | 123 Main Street | - |
| Address Line 2 | text | No | Suite 100 | - |
| City | text | No | City | - |
| State/Province | text | No | State | - |
| Postal Code | text | No | 12345 | - |
| Country | text | No | USA | USA |

##### Contact Information
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Email | email | No | contact@school.edu |
| Phone | tel | No | +1-234-567-8900 |

##### Online Presence
| Field | Type | Required | Placeholder | Help Text |
|-------|------|----------|-------------|-----------|
| Website URL | url | No | https://school.edu | - |
| Facebook URL | url | No | https://facebook.com/schoolname | - |
| Twitter URL | url | No | https://twitter.com/schoolname | - |
| Instagram URL | url | No | https://instagram.com/schoolname | - |
| Logo URL | url | No | https://example.com/logo.png | URL to publicly accessible logo image |

##### Settings
| Field | Type | Required | Options | Default |
|-------|------|----------|---------|---------|
| Timezone | select | No | Eastern Time (ET), Central Time (CT), Mountain Time (MT), Pacific Time (PT), Arizona Time, Alaska Time, Hawaii Time | America/New_York |
| Locale | select | No | English (US), Spanish, French | en_US |
| Status | select | Yes | Active, Inactive, Suspended | active |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Detail | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Teachers

### Overview
Teacher profile management including credentials, assignments, and employment details.

### Views
- **List View:** `/teachers` - Filterable list of all teachers
- **Detail View:** `/teachers/:id` - Teacher profile with classes
- **Create View:** `/teachers/create` - Teacher registration
- **Edit View:** `/teachers/:id/edit` - Update teacher information

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| User Account | UserSelector (searchable) | Yes | Filters persona="teacher". Cannot be changed after creation. |
| Employee ID | text | Yes | e.g., EMP001. Cannot be changed in edit mode. |
| Hire Date | date | Yes | - |
| Termination Date | date | No | - |
| Department | text | No | e.g., Mathematics, Science |
| Job Title | text | No | e.g., Teacher, Lead Teacher |

##### Teaching Credentials
| Field | Type | Required | Placeholder | Options |
|-------|------|----------|-------------|---------|
| Certification Number | text | No | Enter certification number | - |
| Certification Expiry | date | No | - | - |
| Education Level | select | No | - | High School, Associate, Bachelor's, Master's, PhD, Other |
| University | text | No | Enter university name | - |

##### Teaching Assignments
| Field | Type | Required | Help Text |
|-------|------|----------|-----------|
| Grade Levels | checkbox group | Yes | Select all grades this teacher will teach (Grades 1-7) |
| Specializations | text | No | Subject codes separated by commas (e.g., MATH, SCIENCE, ELA) |

##### Employment Details
| Field | Type | Required | Default | Range/Help |
|-------|------|----------|---------|------------|
| Employment Type | select | No | full-time | Full-time, Part-time, Contract, Substitute |
| Work Hours per Week | number | No | 40 | Min: 1, Max: 80 |
| Salary | number | No | - | Min: 0, Step: 0.01. This information is kept confidential. |

##### Emergency Contact
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Contact Name | text | No | Enter full name |
| Contact Phone | tel | No | +1234567890 |
| Relationship | text | No | e.g., Spouse, Parent, Sibling |

##### Additional Information
| Field | Type | Required | Default | Placeholder |
|-------|------|----------|---------|-------------|
| Office Room | text | No | - | e.g., Room 101, Building A |
| Status | select | No | active | Active, Inactive, On Leave, Terminated |
| Bio / Notes | textarea | No | - | Enter bio or additional notes (4 rows) |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 4. Students

### Overview
Student profile management including academic information, medical records, and parent relationships.

### Views
- **List View:** `/students` - Searchable student directory
- **Detail View:** `/students/:id` - Student profile with grades
- **Create View:** `/students/create` - Student enrollment
- **Edit View:** `/students/:id/edit` - Update student record

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Validation/Notes |
|-------|------|----------|------------------|
| Student User Account | UserSelector (searchable) | Yes | Filters persona="student". Cannot be changed after creation. |
| Student ID | text | Yes | e.g., STU001. Cannot be changed in edit mode. |
| Grade Level | select | Yes | Grade 1, Grade 2, Grade 3, Grade 4, Grade 5, Grade 6, Grade 7 |
| Date of Birth | date | Yes | Must be between 5-15 years old. Cannot be changed in edit mode. |
| Gender | select | No | Male, Female, Other, Prefer not to say |
| Enrollment Date | date | Yes | Cannot be changed in edit mode. |
| Graduation Date | date | No | Optional - for graduated students |
| Status | select | Yes | Enrolled (default), Graduated, Transferred, Withdrawn, Suspended |

##### Medical Information
| Field | Type | Required | Placeholder | Rows |
|-------|------|----------|-------------|------|
| Allergies | textarea | No | List any known allergies | 3 |
| Medical Notes | textarea | No | Additional medical information | 3 |

##### Emergency Contact
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Contact Name | text | No | Emergency contact full name |
| Contact Phone | tel | No | +1234567890 |
| Relationship | text | No | e.g., Mother, Guardian |

##### Additional Information
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Photo URL | url | No | https://example.com/photo.jpg |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Detail | ✅ | ✅ | ✅ (own) | ✅ (children) | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 5. Parents

### Overview
Parent/guardian management including contact information, employment, and child relationships.

### Views
- **List View:** `/parents` - Parent directory
- **Detail View:** `/parents/:id` - Parent profile with children
- **Create View:** `/parents/create` - Parent registration
- **Edit View:** `/parents/:id/edit` - Update parent information

### Create/Edit Form

#### Form Sections

##### User Account
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Parent User Account | UserSelector (searchable) | Yes | Filters persona="parent". Cannot be changed after creation. |

##### Contact Information
| Field | Type | Required | Placeholder | Help Text |
|-------|------|----------|-------------|-----------|
| Mobile Phone | tel | No | +1-555-0123 | Parent's primary mobile number |
| Work Phone | tel | No | +1-555-0124 | Parent's work phone number |
| Preferred Contact Method | select | No | - | Email, Phone, SMS, App Notification. How the parent prefers to be contacted. |

##### Employment Information
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Occupation | text | No | e.g., Software Engineer, Teacher, Doctor |
| Workplace | text | No | e.g., Tech Corp, Lincoln Elementary |

##### Preferences & Permissions
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| Emergency Contact | checkbox | No | false | Can be contacted in case of emergencies |
| Pickup Authorized | checkbox | No | false | Authorized to pick up students from school |
| Receives Newsletter | checkbox | No | true | Subscribe to school newsletters and updates |

##### Children (Edit Mode Only)
**Link Student Dialog:**
| Field | Type | Required | Options | Description |
|-------|------|----------|---------|-------------|
| Student ID | text | Yes | - | Enter student UUID |
| Relationship Type | select | Yes | Mother, Father, Guardian, Stepmother, Stepfather, Grandparent, Foster Parent, Other | - |
| Primary Contact | checkbox | No | - | Is this the primary contact? |
| Legal Custody | checkbox | No | - | Has legal custody? |
| Pickup Permission | checkbox | No | - | Has pickup permission? |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ❌ | ❌ | ❌ |
| View Detail | ✅ | ✅ | ❌ | ✅ (own) | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 6. Subjects

### Overview
Academic subject management with grade levels, categories, and visual customization.

### Views
- **List View:** `/subjects` - Grid view of all subjects
- **Detail View:** `/subjects/:id` - Subject details with classes
- **Create View:** `/subjects/create` - Add new subject
- **Edit View:** `/subjects/:id/edit` - Modify subject

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder | Validation | Help Text |
|-------|------|----------|-------------|------------|-----------|
| Subject Code | text | Yes | e.g., MATH, ELA, SCIENCE | Uppercase letters, numbers, and underscores only | Cannot be changed after creation |
| Subject Name | text | Yes | e.g., Mathematics | - | - |
| Description | textarea | No | Brief description of the subject... | - | 3 rows |

##### Classification
| Field | Type | Required | Default | Options | Description |
|-------|------|----------|---------|---------|-------------|
| Category | select | Yes | core | Core, Elective, Enrichment, Remedial, Other | - |
| Subject Type | select | No | - | Academic, Arts, Physical Education, Technical, Other | - |
| Is Required | checkbox | No | false | - | Subject is mandatory for all students |
| Active | checkbox | No | false | - | Subject is currently active and available |

##### Grade Levels
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| Grade Levels | checkbox group | Yes | All selected | Grades 1-7. Select at least one grade level. |

##### Display Properties
| Field | Type | Required | Default | Pattern | Help Text |
|-------|------|----------|---------|---------|-----------|
| Color | color + text | No | #2196F3 | ^#[0-9A-Fa-f]{6}$ | Hex color format (#RRGGBB). "Use Default" button available. |
| Icon | text | No | 🔢 | - | Emoji or icon identifier (maxlength: 50). "Use Default" button available. |
| Display Order | number | No | 0 | Min: 0 | Lower numbers appear first in sorted lists |

##### Academic Properties
| Field | Type | Required | Placeholder | Help Text |
|-------|------|----------|-------------|-----------|
| Credits | number | No | Optional | Min: 0, Step: 0.5. Credit hours for this subject (optional) |

**Preview Section:** Shows preview card with icon, code, name, category badge, required badge, active badge, and grade levels.

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 7. Rooms

### Overview
Facility and classroom management with capacity, equipment tracking, and availability status.

### Views
- **List View:** `/rooms` - Filterable room directory
- **Detail View:** `/rooms/:id` - Room details with schedule
- **Create View:** `/rooms/create` - Register new room
- **Edit View:** `/rooms/:id/edit` - Update room information

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder | Pattern | Help Text |
|-------|------|----------|-------------|---------|-----------|
| Room Number | text | Yes | e.g., 101, LAB-A, GYM-1 | [A-Za-z0-9\s\-]+ | Alphanumeric, spaces, and hyphens allowed. Cannot be changed after creation. Maxlength: 50 |
| Room Name | text | No | e.g., Math Classroom A | - | Maxlength: 200 |
| Description | textarea | No | Describe the room... | - | 3 rows |

##### Location
| Field | Type | Required | Placeholder | Help Text |
|-------|------|----------|-------------|-----------|
| Building | text | No | e.g., Main Building | Maxlength: 100 |
| Floor | number | No | Floor number | -2 to 10 (negative for basement) |

##### Classification
| Field | Type | Required | Options | Help Text |
|-------|------|----------|---------|-----------|
| Room Type | select | Yes | Classroom, Laboratory, Gymnasium, Library, Office, Cafeteria | - |
| Capacity | number | Yes | 30 | Min: 1, Max: 1000. Number of people. |
| Area (sq ft) | number | No | 800.5 | Min: 0, Step: 0.1 |

##### Equipment & Features
| Field | Type | Description |
|-------|------|-------------|
| Equipment | Dynamic list | Add/remove equipment items. Placeholder: "Equipment item" |
| Features | Dynamic list | Add/remove features. Placeholder: "Feature" |

##### Status
| Field | Type | Help Text |
|-------|------|-----------|
| Active | checkbox | Room can be used for scheduling |
| Available | checkbox | Room is currently available |

##### Display Properties
| Field | Type | Default | Pattern | Help Text |
|-------|------|---------|---------|-----------|
| Color | color + text | #4CAF50 | ^#[0-9A-Fa-f]{6}$ | Hex format (#RRGGBB). "Use Default" button available. |
| Icon | text | 🏫 | - | Emoji or icon identifier (maxlength: 50). "Use Default" button available. |
| Display Order | number | 0 | Min: 0 | - |

**Preview Section:** Shows room card with icon, room number, name, type badge, and capacity.

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 8. Classes

### Overview
Class section management linking teachers, subjects, students, and schedules.

### Views
- **List View:** `/classes` - Filterable class list
- **Detail View:** `/classes/:id` - Class roster and schedule
- **Create View:** `/classes/create` - Create new class section
- **Edit View:** `/classes/:id/edit` - Update class details

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder | Notes |
|-------|------|----------|-------------|-------|
| Subject | select | Yes | Select a subject | Shows subject name and code |
| Class Name | text | Yes | e.g., Mathematics Grade 5 Quarter 1 Section A | - |
| Grade Level | select | Yes | - | Grade 1-7 |
| Quarter | select | Yes | - | Quarter 1, Quarter 2, Quarter 3, Quarter 4 |
| Academic Year | select | Yes | - | Previous year, Current year (marked), Next year |
| Section | text | Yes | e.g., A, B, 1, 2 | Maxlength: 5, uppercase. Single letter or number to identify the section. |
| Class Code Preview | read-only | - | - | Format: SUBJECT-GRADE-QUARTER-SECTION |
| Description | textarea | No | Optional description of the class | 3 rows |

##### Assignments
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Teacher | select | Yes | Shows teacher name and specialization |
| Room | select | No | Shows room number, name, and type |

##### Capacity
| Field | Type | Required | Default | Range |
|-------|------|----------|---------|-------|
| Maximum Students | number | Yes | 30 | Min: 1, Max: 100 |
| Current Enrollment | read-only | - | - | Edit mode only |

##### Schedule (Optional)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Add class schedule | checkbox | - | Enable to add schedule |
| Days | checkbox group | Yes (if schedule enabled) | Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday |
| Start Time | time | Yes (if schedule enabled) | Default: 09:00 |
| End Time | time | Yes (if schedule enabled) | Default: 10:30 |
| Preview | read-only | - | Shows formatted schedule |

##### Display Settings
| Field | Type | Default | Pattern | Help Text |
|-------|------|---------|---------|-----------|
| Color | color + text | #3B82F6 | ^#[0-9A-Fa-f]{6}$ | Optional color for visual identification. "Clear" button available. |
| Display Order | number | 0 | Min: 0 | Lower numbers appear first (default: 0) |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 9. Lessons

### Overview
Lesson plan management with objectives, activities, materials, and assessments.

### Views
- **List View:** `/lessons` - Calendar and list view of lessons
- **Detail View:** `/lessons/:id` - Complete lesson plan
- **Create View:** `/lessons/create` - Create lesson plan
- **Edit View:** `/lessons/:id/edit` - Update lesson plan

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder | Range/Notes |
|-------|------|----------|-------------|-------------|
| Title | text | Yes | Enter lesson title | Maxlength: 200 |
| Description | textarea | No | Enter lesson description | 3 rows |
| Scheduled Date | date | Yes | - | - |
| Duration (minutes) | number | Yes | - | Min: 1, Max: 240 |
| Class | Searchable dropdown | Yes | Search by class code (e.g., MATH-3-Q1-A) | Shows class code, name, grade, quarter |
| Teacher | Searchable dropdown | Yes | Search by employee ID | Shows employee ID, name, department |
| Subject | Searchable dropdown | Yes | Search by subject code (e.g., MATH) | Shows subject code and name |
| Color | color picker | No | - | Default: #2563eb. Help text: "for calendar" |

##### Lesson Plan
| Field | Type | Required | Placeholder | Rows |
|-------|------|----------|-------------|------|
| Introduction | textarea | No | Describe how you'll introduce the topic... | 3 |
| Main Activity | textarea | No | Describe the main learning activity... | 4 |
| Assessment | textarea | No | How will you assess student understanding? | 3 |
| Homework | textarea | No | Homework assignments... | 2 |
| Notes | textarea | No | Additional notes... | 2 |

##### Learning Objectives
| Field | Type | Description |
|-------|------|-------------|
| Learning Objectives | Dynamic list | Add/remove objectives. Placeholder: "Learning objective..." |

##### Materials Needed
| Field | Type | Description |
|-------|------|-------------|
| Materials Needed | Dynamic list | Add/remove materials. Placeholder: "Material needed..." |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete | ✅ (soft) | ✅ (soft) | ❌ | ❌ | ❌ |

---

## 10. Assessments

### Overview
Assessment and grading management for tests, quizzes, projects, and assignments.

### Views
- **List View:** `/assessments` - Filterable assessment list
- **Detail View:** `/assessments/:id` - Assessment details and grades
- **Create View:** `/assessments/create` - Create assessment
- **Edit View:** `/assessments/:id/edit` - Update assessment

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Title | text | Yes | Chapter 5 Test |
| Description | textarea | No | Describe the assessment... (3 rows) |
| Type | select | Yes | - |
| Quarter | select | Yes | - |

**Type Options:** Test, Quiz, Project, Assignment, Exam, Presentation, Homework, Lab, Other
**Quarter Options:** Quarter 1, Quarter 2, Quarter 3, Quarter 4

##### Assignment Details
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Student | select | Yes | Disabled in edit mode |
| Class | select | Yes | Disabled in edit mode |
| Subject | select | Yes | Disabled in edit mode |
| Teacher | select | Yes | Disabled in edit mode |

##### Dates and Grading
| Field | Type | Required | Range/Default |
|-------|------|----------|---------------|
| Assessment Date | date | Yes | - |
| Due Date | date | No | - |
| Total Points | number | Yes | Min: 0, Step: 0.1, Placeholder: "100" |
| Weight | number | No | Min: 0, Max: 10, Step: 0.1, Placeholder: "1.0" |
| Extra Credit | checkbox | No | false |
| Makeup Assessment | checkbox | No | false |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ (own) | ✅ (children) | ❌ |
| View Detail | ✅ | ✅ | ✅ (own) | ✅ (children) | ❌ |
| Create | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit | ✅ | ✅ | ❌ | ❌ | ❌ |
| Grade | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 11. Attendance

### Overview
Daily attendance tracking with status, check-in/out times, and bulk marking capabilities.

### Views
- **List View:** `/attendance` - Calendar and filter view
- **Detail View:** `/attendance/:id` - Attendance record details
- **Create/Bulk Mark:** `/attendance/create` - Mark attendance for a class
- **Edit View:** `/attendance/:id/edit` - Update attendance record

### Create/Edit Form

#### Two Modes:

##### Mode 1: Single Record Edit

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Student | read-only | - | Display only |
| Date | read-only | - | Display only |
| Status | select | Yes | Present, Absent, Tardy, Excused, Sick |
| Check In Time | time | No | - |
| Check Out Time | time | No | - |
| Notes | textarea | No | Optional notes about this attendance record... (3 rows) |

##### Mode 2: Bulk Attendance Marking

**Class Information:**
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Class | Searchable dropdown | Yes | Search by class code (e.g., MATH-3-Q1-A) |
| Date | date | Yes | - |

**Student Attendance Table** (after loading students):

For each student:
| Field | Type | Notes |
|-------|------|-------|
| Student | read-only | Shows name and student ID |
| Status | select | Options: Present, Absent, Tardy, Excused, Sick |
| Check In | time | Disabled unless status is present or tardy |
| Check Out | time | Disabled unless check-in time is set |
| Notes | text | Optional notes... |

**Quick Actions:**
- Mark All Present button
- Clear All button

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ (own) | ✅ (children) | ❌ |
| View Detail | ✅ | ✅ | ✅ (own) | ✅ (children) | ❌ |
| Create/Mark | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit | ✅ | ✅ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 12. Events

### Overview
School event calendar management with RSVP, recurring events, and audience targeting.

### Views
- **List View:** `/events` - Calendar view with filters
- **Detail View:** `/events/:id` - Event details with RSVP
- **Create View:** `/events/create` - Create new event
- **Edit View:** `/events/:id/edit` - Update event

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder | Range |
|-------|------|----------|-------------|-------|
| Title | text | Yes | Event title | Maxlength: 200 |
| Description | textarea | No | Event description | 4 rows |
| Event Type | select | Yes | - | See options below |
| Status | select | No | scheduled (default) | See options below |
| Calendar Color | color picker | No | #3B82F6 (default) | Choose a color for calendar display |

**Event Type Options:** Assembly, Exam, Holiday, Meeting, Parent Conference, Field Trip, Sports, Performance, Workshop, Other
**Status Options:** Scheduled, In Progress, Completed, Cancelled, Postponed

##### Date & Time
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Start Date | date | Yes | - |
| End Date | date | Yes | - |
| All Day Event | checkbox | No | - |
| Start Time | time | No | Hidden if all day |
| End Time | time | No | Hidden if all day |

##### Location
| Field | Type | Required | Placeholder | Range |
|-------|------|----------|-------------|-------|
| Location | text | No | e.g., Main Auditorium, Gymnasium, etc. | Maxlength: 255 |

##### Target Audience
| Field | Type | Required | Options | Notes |
|-------|------|----------|---------|-------|
| Audience Type | select | No | Not specified, All School, Specific Grade Levels, Specific Classes, Custom | - |
| Grade Levels | checkbox group | Conditional | Grades 1-7 | Shown when "Specific Grade Levels" selected |

##### Recurring Event
| Field | Type | Required | Options | Notes |
|-------|------|----------|---------|-------|
| This is a recurring event | checkbox | No | - | - |
| Recurrence Pattern | select | Conditional | Daily, Weekly, Monthly, Yearly | Shown if recurring |
| Recurrence End Date | date | Conditional | - | Shown if recurring |

##### RSVP Settings
| Field | Type | Required | Placeholder | Notes |
|-------|------|----------|-------------|-------|
| Require RSVP for this event | checkbox | No | - | - |
| Maximum Attendees | number | Conditional | Leave empty for unlimited | Min: 1. Shown if RSVP required |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit | ✅ | ✅ | ❌ | ❌ | ❌ |
| RSVP | ✅ | ✅ | ✅ | ✅ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 13. Activities

### Overview
Extracurricular activity management including clubs, sports, and enrichment programs.

### Views
- **List View:** `/activities` - Grid/list of all activities
- **Detail View:** `/activities/:id` - Activity details with roster
- **Create View:** `/activities/create` - Register new activity
- **Edit View:** `/activities/:id/edit` - Update activity

### Create/Edit Form

#### Form Sections

##### Basic Information
| Field | Type | Required | Placeholder | Range |
|-------|------|----------|-------------|-------|
| Activity Name | text | Yes | e.g., Basketball Team, Chess Club, Art Studio | Maxlength: 255 |
| Activity Code | text | No | e.g., BBALL-01, CHESS-01 | Maxlength: 20. Optional unique identifier |
| Activity Type | select | Yes | - | Sports, Club, Art, Music, Academic, Other |
| Category | text | No | e.g., Team Sports, STEM, Visual Arts | Maxlength: 100. Optional subcategory for organization |
| Description | textarea | No | Describe the activity, its goals, and what students will learn | 4 rows |
| Display Color | color picker | No | #3B82F6 (default) | Choose a color for visual identification |

##### Eligibility
| Field | Type | Required | Help Text |
|-------|------|----------|-----------|
| Grade Levels | checkbox group | Yes | Select all grade levels eligible for this activity (Grades 1-7) |
| Minimum Participants | number | No | Minimum enrollment to run activity. Min: 1 |
| Maximum Participants | number | No | Maximum enrollment capacity. Min: 1 |

##### Schedule
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Start Date | date | No | - |
| End Date | date | No | - |
| Define weekly schedule | checkbox | No | - |
| Days of Week | checkbox group | Conditional | Monday-Sunday. Shown when schedule enabled |
| Start Time | time | Conditional | Shown when schedule enabled |
| End Time | time | Conditional | Shown when schedule enabled |

##### Location
| Field | Type | Required | Placeholder | Range |
|-------|------|----------|-------------|-------|
| Location | text | No | e.g., Main Gym, Art Room 101, Music Hall | Maxlength: 255 |

##### Financial Information
| Field | Type | Required | Placeholder | Help Text |
|-------|------|----------|-------------|-----------|
| Activity Cost | number | No | 0.00 | Min: 0, Step: 0.01. Main cost for participation |
| Registration Fee | number | No | 0.00 | Min: 0, Step: 0.01. One-time registration fee |
| Equipment Fee | number | No | 0.00 | Min: 0, Step: 0.01. Cost for equipment or materials |

##### Requirements
| Field | Type | Required | Placeholder | Help Text |
|-------|------|----------|-------------|-----------|
| Prerequisites/Requirements | textarea | No | Enter each requirement on a new line | 3 rows. One requirement per line (e.g., 'Parent consent required') |
| Equipment Needed | textarea | No | Enter each item on a new line | 3 rows. One item per line (e.g., 'Basketball shoes', 'Calculator') |
| Uniform Required | checkbox | No | - |

##### Contact Information
| Field | Type | Required | Placeholder |
|-------|------|----------|-------------|
| Contact Email | email | No | activity@example.com |
| Contact Phone | tel | No | +1234567890 |
| Information for Parents | textarea | No | Important information for parents about this activity (3 rows) |

##### Status & Settings
| Field | Type | Required | Default | Options | Help Text |
|-------|------|----------|---------|---------|-----------|
| Status | select | No | active | Active, Full, Cancelled, Completed | - |
| Registration Open | checkbox | No | true | - | Allow students to register for this activity |
| Featured Activity | checkbox | No | false | - | Highlight this activity on the main activities page |

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Detail | ✅ | ✅ | ✅ | ✅ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage Roster | ✅ | ✅ | ❌ | ❌ | ❌ |
| Register | - | - | ✅ | ✅ (for children) | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 14. Vendors

### Overview
External vendor management for school services and suppliers.

### Views
- **List View:** `/vendors` - Vendor directory
- **Detail View:** `/vendors/:id` - Vendor profile and contracts

### Implementation Status
⚠️ **Form Not Yet Implemented** - Only list view exists. Create/edit forms are pending implementation.

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View List | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Detail | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 15. Merits

### Overview
Student merit and reward system for tracking achievements and positive behavior.

### Views
- **List View:** `/merits` - Merit leaderboard and history
- **Detail View:** `/merits/:id` - Merit details

### Implementation Status
⚠️ **Form Not Yet Implemented** - Merit awarding interface is pending implementation.

### User Roles & Permissions

| Action | Administrator | Teacher | Student | Parent | Vendor |
|--------|---------------|---------|---------|--------|--------|
| View Leaderboard | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Detail | ✅ | ✅ | ✅ (own) | ✅ (children) | ❌ |
| Award Merits | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit | ❌ | ❌ | ❌ | ❌ | ❌ |
| Delete | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Role-Based Access Control Matrix

### Complete RBAC Overview

| # | Feature | View/List | Create | Edit | Delete | Notes |
|---|---------|-----------|--------|------|--------|-------|
| 1 | **Users** | Administrator | Administrator | Administrator | Administrator | Detail view: All authenticated users (own profile only for non-admins) |
| 2 | **Schools** | Administrator | Administrator | Administrator | N/A | Complete admin-only feature |
| 3 | **Teachers** | Administrator | Administrator | Administrator | N/A | Detail view: All authenticated users |
| 4 | **Students** | Administrator, Teacher | Administrator | Administrator | Administrator | Detail view: All authenticated users |
| 5 | **Parents** | Administrator, Teacher | Administrator | Administrator | N/A | Detail view: All authenticated users |
| 6 | **Subjects** | Administrator, Teacher | Administrator | Administrator | N/A | Detail view: All authenticated users |
| 7 | **Rooms** | Administrator, Teacher | Administrator | Administrator | N/A | Detail view: All authenticated users |
| 8 | **Classes** | Administrator, Teacher, Student, Parent | Administrator | Administrator | N/A | Detail view: All authenticated users |
| 9 | **Lessons** | Administrator, Teacher | Administrator, Teacher | Administrator, Teacher | Yes (soft delete) | Detail view: All authenticated users |
| 10 | **Assessments** | Administrator, Teacher, Student, Parent | Administrator, Teacher | Administrator, Teacher | N/A | Grading: Administrator, Teacher only |
| 11 | **Attendance** | Administrator, Teacher, Student, Parent | Administrator, Teacher | Administrator, Teacher | N/A | Mark attendance: Administrator, Teacher only |
| 12 | **Events** | Administrator, Teacher, Student, Parent | Administrator, Teacher | Administrator, Teacher | N/A | All roles can view events |
| 13 | **Activities** | Administrator, Teacher, Student, Parent | Administrator | Administrator | N/A | Roster management: Administrator, Teacher |
| 14 | **Vendors** | Administrator | Administrator | Administrator | N/A | Complete admin-only feature |
| 15 | **Merits** | Administrator, Teacher, Student, Parent | Administrator, Teacher | N/A | N/A | Award merits: Administrator, Teacher; Leaderboard: All authenticated |

### Role Summary

#### Administrator
- **Access Level:** Full system access
- **Can View:** All features
- **Can Create:** All features
- **Can Edit:** All features
- **Can Delete:** Users, Students only
- **Special Privileges:** User management, school configuration, system settings

#### Teacher
- **Access Level:** Academic management
- **Can View:** Teachers, Students, Parents, Subjects, Rooms, Classes, Lessons, Assessments, Attendance, Events, Activities, Merits
- **Can Create:** Lessons, Assessments, Attendance, Events
- **Can Edit:** Lessons, Assessments, Attendance, Events
- **Can Delete:** Lessons (soft delete)
- **Special Privileges:** Grade students, mark attendance, manage class roster

#### Student
- **Access Level:** Read-only (personal data)
- **Can View:** Own profile, Classes, Assessments (own), Attendance (own), Events, Activities, Merits
- **Can Create:** None
- **Can Edit:** Own profile only
- **Can Delete:** None
- **Special Privileges:** Register for activities, RSVP to events

#### Parent
- **Access Level:** Read-only (children's data)
- **Can View:** Own profile, Children's profiles, Classes, Assessments (children), Attendance (children), Events, Activities, Merits
- **Can Create:** None
- **Can Edit:** Own profile only
- **Can Delete:** None
- **Special Privileges:** Register children for activities, RSVP to events, view children's grades

#### Vendor
- **Access Level:** Minimal (vendor-specific)
- **Can View:** Vendors (own profile)
- **Can Create:** None
- **Can Edit:** Own profile only
- **Can Delete:** None
- **Special Privileges:** View event attendance (if relevant), supply orders

---

## Common Form Patterns

### Field Types Used Across Features

1. **Text Inputs:** text, email, tel, url, password
2. **Numeric Inputs:** number (with min, max, step validation)
3. **Date/Time Inputs:** date, time
4. **Selection Inputs:** select dropdown, checkbox, checkbox group, radio
5. **Text Areas:** textarea (multiline text with configurable rows)
6. **Color Pickers:** color input with hex validation
7. **Searchable Dropdowns:** Custom components (UserSelector, ClassSelector, etc.)
8. **Dynamic Lists:** Add/remove items for arrays (objectives, materials, equipment)

### Common Validation Patterns

1. **Required Fields:** Marked with asterisk (*), HTML5 `required` attribute
2. **Email Validation:** HTML5 email type
3. **Phone Validation:** tel type with placeholder format
4. **URL Validation:** url type
5. **Pattern Matching:** Regex patterns for codes, slugs, colors
6. **Range Validation:** min/max for numbers, dates
7. **Length Limits:** maxlength for text inputs
8. **Custom Validation:** Age ranges, grade levels, business rules

### Form Sections Organization

Most forms use 3-7 logical sections:
1. **Basic/Primary Information** - Core identifying fields
2. **Classification/Type** - Category, type, status
3. **Details/Extended** - Additional descriptive information
4. **Settings/Preferences** - Configuration options
5. **Display/Visual** - Colors, icons, ordering
6. **Preview** - Visual representation (Subjects, Rooms)

### Edit Mode Restrictions

Certain fields are disabled in edit mode to preserve data integrity:
- **IDs:** User email, Student ID, Employee ID, Subject Code, Room Number
- **Dates:** Date of Birth, Enrollment Date (students)
- **Linked Entities:** User accounts (after creation)

### Default Values

Common defaults across forms:
- **Status:** "active"
- **Colors:** Blue shades (#2196F3, #3B82F6, #2563eb)
- **Booleans:** Most checkboxes default to false, except "Receives Newsletter" (true)
- **Numbers:** Capacity (30), Work Hours (40), Display Order (0)

---

## Implementation Status

### Features Fully Implemented (13/15)

✅ **Complete Form Implementation:**
1. Users
2. Schools
3. Teachers
4. Students
5. Parents
6. Subjects
7. Rooms
8. Classes
9. Lessons
10. Assessments
11. Attendance
12. Events
13. Activities

### Features Pending Implementation (2/15)

⚠️ **Forms Not Yet Implemented:**
14. Vendors - List view exists, form pending
15. Merits - List view exists, award interface pending

---

## Appendix

### File Locations

**Frontend Components:**
- Views: `/frontend/src/views/`
- Forms: `/frontend/src/components/`
- Router: `/frontend/src/router/index.ts`
- Stores: `/frontend/src/stores/`

**Documentation:**
- Feature Plans: `/docs/features/`
- API Docs: `/docs/api/`
- Schema Docs: `/docs/schema/`

### Related Documentation

- [CLAUDE.md](/CLAUDE.md) - Project overview and development guide
- [Backend API Documentation](/docs/api/) - API endpoints and schemas
- [Database Schema](/docs/schema/) - Complete database structure
- [Feature Plans](/docs/features/) - Detailed feature specifications

---

**Document Generated:** October 31, 2025
**System Version:** 1.0.0
**Database:** PostgreSQL 14
**Frontend:** Vue 3.4.29
**Backend:** Python 3.11 + FastAPI

---

*This documentation was auto-generated by analyzing Vue component files and router configurations. For the most up-to-date information, refer to the source code in the repository.*
