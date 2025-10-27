# CREATE Functionality Test Plan

**Project:** Green School Management System  
**Test Type:** Create Form Validation & Submission  
**Date:** 2025-10-27

---

## Test Objective

Validate that all CREATE forms work correctly with sample data and successfully create records in the system.

---

## Test Strategy

For each feature:
1. Navigate to create form
2. Fill all required fields with valid sample data
3. Submit the form
4. Verify success message
5. Verify record appears in list
6. Capture screenshots at each step

---

## Features & Sample Data

### 01. Users

**Route:** `/users/create`

**Sample Data:**
```json
{
  "email": "john.doe@greenschool.edu",
  "first_name": "John",
  "last_name": "Doe",
  "role": "teacher",
  "phone": "+1234567890",
  "is_active": true
}
```

**Validation:**
- Email format valid
- All required fields filled
- Success message appears
- User appears in `/users` list

---

### 02. Schools

**Route:** `/schools/create`

**Sample Data:**
```json
{
  "name": "Green Valley Primary School",
  "code": "GVPS001",
  "address": "123 Education Street",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62701",
  "country": "USA",
  "phone": "+1-555-0100",
  "email": "info@greenvalley.edu",
  "principal_name": "Dr. Sarah Johnson",
  "established_year": 2010,
  "student_capacity": 500
}
```

**Validation:**
- School code unique
- All required fields filled
- Success message appears
- School appears in `/schools` list

---

### 03. Teachers

**Route:** `/teachers/create`

**Sample Data:**
```json
{
  "user_id": "{select-from-dropdown}",
  "employee_id": "TCH001",
  "hire_date": "2024-01-15",
  "department": "Mathematics",
  "qualification": "Master of Education",
  "specialization": "Secondary Mathematics",
  "years_of_experience": 5,
  "employment_type": "full_time",
  "salary_grade": "Grade A"
}
```

**Validation:**
- User selected from dropdown
- Employee ID unique
- Date format valid
- Success message appears
- Teacher appears in `/teachers` list

---

### 04. Students

**Route:** `/students/create`

**Sample Data:**
```json
{
  "first_name": "Emma",
  "last_name": "Wilson",
  "date_of_birth": "2015-03-20",
  "gender": "female",
  "grade": 3,
  "admission_number": "STU2024001",
  "admission_date": "2024-09-01",
  "blood_group": "A+",
  "address": "456 Student Lane",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62702",
  "emergency_contact_name": "Mary Wilson",
  "emergency_contact_phone": "+1-555-0201",
  "medical_conditions": "None"
}
```

**Validation:**
- Grade between 1-7
- Admission number unique
- Date of birth valid (age appropriate)
- Success message appears
- Student appears in `/students` list

---

### 05. Parents

**Route:** `/parents/create`

**Sample Data:**
```json
{
  "user_id": "{select-from-dropdown}",
  "relationship": "mother",
  "occupation": "Software Engineer",
  "employer": "Tech Corp",
  "work_phone": "+1-555-0301",
  "home_phone": "+1-555-0302",
  "address": "789 Parent Avenue",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62703",
  "emergency_contact": true
}
```

**Validation:**
- User selected from dropdown
- Relationship type valid
- Success message appears
- Parent appears in `/parents` list

---

### 06. Subjects

**Route:** `/subjects/create`

**Sample Data:**
```json
{
  "name": "Mathematics",
  "code": "MATH101",
  "description": "Basic Mathematics for Grade 3",
  "grade": 3,
  "credits": 4,
  "subject_type": "core",
  "is_mandatory": true
}
```

**Validation:**
- Subject code unique
- Grade between 1-7
- Success message appears
- Subject appears in `/subjects` list

---

### 07. Rooms

**Route:** `/rooms/create`

**Sample Data:**
```json
{
  "room_number": "101",
  "room_name": "Science Lab A",
  "room_type": "laboratory",
  "building": "Main Building",
  "floor": 1,
  "capacity": 30,
  "has_projector": true,
  "has_whiteboard": true,
  "has_computers": true,
  "is_accessible": true
}
```

**Validation:**
- Room number unique
- Capacity > 0
- Success message appears
- Room appears in `/rooms` list

---

### 08. Classes

**Route:** `/classes/create`

**Sample Data:**
```json
{
  "name": "Grade 3A",
  "grade": 3,
  "section": "A",
  "academic_year": "2024-2025",
  "teacher_id": "{select-from-dropdown}",
  "room_id": "{select-from-dropdown}",
  "max_students": 30,
  "schedule": "Morning Shift"
}
```

**Validation:**
- Grade between 1-7
- Teacher and room selected
- Success message appears
- Class appears in `/classes` list

---

### 09. Lessons

**Route:** `/lessons/create`

**Sample Data:**
```json
{
  "title": "Introduction to Fractions",
  "class_id": "{select-from-dropdown}",
  "subject_id": "{select-from-dropdown}",
  "teacher_id": "{select-from-dropdown}",
  "lesson_date": "2024-11-01",
  "start_time": "09:00",
  "end_time": "10:00",
  "room_id": "{select-from-dropdown}",
  "lesson_type": "lecture",
  "description": "Basic concepts of fractions",
  "objectives": "Understand numerator and denominator"
}
```

**Validation:**
- All dropdowns selected
- Date and time valid
- End time after start time
- Success message appears
- Lesson appears in `/lessons` list

---

### 10. Assessments

**Route:** `/assessments/create`

**Sample Data:**
```json
{
  "title": "Math Quiz - Fractions",
  "class_id": "{select-from-dropdown}",
  "subject_id": "{select-from-dropdown}",
  "assessment_type": "quiz",
  "assessment_date": "2024-11-15",
  "total_marks": 100,
  "passing_marks": 40,
  "duration_minutes": 60,
  "quarter": "Q1",
  "description": "Quiz on fraction concepts",
  "instructions": "Answer all questions"
}
```

**Validation:**
- Total marks > 0
- Passing marks < total marks
- Quarter valid (Q1-Q4)
- Success message appears
- Assessment appears in `/assessments` list

---

### 11. Attendance

**Route:** `/attendance/mark`

**Sample Data:**
```json
{
  "class_id": "{select-from-dropdown}",
  "attendance_date": "2024-10-27",
  "students": [
    {
      "student_id": "{student-1}",
      "status": "present"
    },
    {
      "student_id": "{student-2}",
      "status": "present"
    },
    {
      "student_id": "{student-3}",
      "status": "absent",
      "reason": "Sick"
    }
  ]
}
```

**Validation:**
- Class selected
- Date valid
- At least one student marked
- Success message appears
- Attendance appears in `/attendance` list

---

### 12. Events

**Route:** `/events/create`

**Sample Data:**
```json
{
  "title": "Annual Sports Day",
  "event_type": "sports",
  "event_date": "2024-12-15",
  "start_time": "08:00",
  "end_time": "16:00",
  "location": "School Playground",
  "description": "Annual sports competition for all grades",
  "organizer": "Sports Department",
  "max_participants": 200,
  "is_mandatory": false,
  "target_grades": [1, 2, 3, 4, 5, 6, 7]
}
```

**Validation:**
- Date in future
- End time after start time
- Success message appears
- Event appears in `/events` list

---

### 13. Activities

**Route:** `/activities/create`

**Sample Data:**
```json
{
  "name": "Chess Club",
  "activity_type": "club",
  "description": "Learn and play chess",
  "instructor_name": "Mr. Robert Brown",
  "schedule": "Every Tuesday 3:00 PM - 4:30 PM",
  "location": "Room 205",
  "max_participants": 20,
  "fee": 50.00,
  "start_date": "2024-11-01",
  "end_date": "2025-05-31",
  "target_grades": [4, 5, 6, 7]
}
```

**Validation:**
- End date after start date
- Max participants > 0
- Fee >= 0
- Success message appears
- Activity appears in `/activities` list

---

### 14. Vendors

**Route:** `/vendors/create`

**Sample Data:**
```json
{
  "name": "ABC Stationery Supplies",
  "vendor_code": "VEN001",
  "vendor_type": "supplier",
  "contact_person": "Michael Chen",
  "email": "michael@abcstationery.com",
  "phone": "+1-555-0400",
  "address": "321 Business Park",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62704",
  "tax_id": "TAX123456",
  "payment_terms": "Net 30",
  "is_active": true
}
```

**Validation:**
- Vendor code unique
- Email format valid
- Success message appears
- Vendor appears in `/vendors` list

---

### 15. Merits

**Route:** `/merits/award`

**Sample Data:**
```json
{
  "student_id": "{select-from-dropdown}",
  "merit_type": "academic_excellence",
  "points": 10,
  "reason": "Excellent performance in Math Quiz",
  "awarded_by": "{teacher-id}",
  "awarded_date": "2024-10-27",
  "quarter": "Q1"
}
```

**Validation:**
- Student selected
- Points > 0
- Quarter valid (Q1-Q4)
- Success message appears
- Merit appears in `/merits` list

---

## Test Execution Steps

### For Each Feature:

1. **Navigate to Create Form**
   ```
   Screenshot: {feature}-01-create-form-empty.png
   ```

2. **Fill Form with Sample Data**
   - Enter all required fields
   - Select from dropdowns where applicable
   ```
   Screenshot: {feature}-02-create-form-filled.png
   ```

3. **Submit Form**
   - Click Submit/Create button
   - Wait for response
   ```
   Screenshot: {feature}-03-form-submitting.png
   ```

4. **Verify Success**
   - Check for success message
   - Note any error messages
   ```
   Screenshot: {feature}-04-success-message.png
   ```

5. **Verify in List**
   - Navigate to list view
   - Find newly created record
   - Verify data matches
   ```
   Screenshot: {feature}-05-record-in-list.png
   ```

---

## Success Criteria

For each feature, the test passes if:
- ✅ Form loads without errors
- ✅ All fields accept sample data
- ✅ Form submits successfully
- ✅ Success message displays
- ✅ Record appears in list view
- ✅ Data matches what was entered

---

## Test Data Dependencies

### Prerequisites:
1. **Users** must be created first (needed for Teachers, Parents)
2. **Teachers** needed for Classes, Lessons
3. **Subjects** needed for Lessons, Assessments
4. **Rooms** needed for Classes, Lessons
5. **Classes** needed for Lessons, Assessments, Attendance
6. **Students** needed for Attendance, Merits

### Recommended Test Order:
1. Schools
2. Users
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
14. Vendors
15. Merits

---

## Expected Results

### Screenshots Per Feature: 5
- Empty form
- Filled form
- Submitting state
- Success message
- Record in list

### Total Screenshots: 75 (15 features × 5 screenshots)

---

## Automation Script

See: `tests/ux-create-forms.spec.ts`

Run with:
```bash
npx playwright test tests/ux-create-forms.spec.ts
```

---

**Created:** 2025-10-27  
**Status:** Ready for Execution
