# Updated Database Schema

This document provides an overview of the database schema, based on the analysis of the SQLAlchemy models in `backend/models`.

## Core Models

### `BaseModel`
All models inherit from `BaseModel`, which provides the following common fields:
- `id`: UUID (Primary Key)
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `deleted_at`: Timestamp (for soft deletes)
- `is_deleted`: Boolean (for soft deletes)

### `School`
This is the central model for the multi-tenant architecture.

| Column | Type | Relationships | Description |
|---|---|---|---|
| `id` | UUID | | Primary Key |
| `name` | String | | Name of the school |
| `address` | String | | Physical address of the school |
| `phone_number` | String | | Contact phone number |
| `email` | String | | Contact email address |
| `website` | String | | School's website URL |
| `users` | `User` | One-to-Many | All users associated with this school |
| `subjects` | `Subject` | One-to-Many | All subjects taught at this school |
| `classes` | `Class` | One-to-Many | All classes held at this school |

### `User`
Represents a user in the system.

| Column | Type | Relationships | Description |
|---|---|---|---|
| `id` | UUID | | Primary Key |
| `school_id` | UUID | Many-to-One with `School` | The school this user belongs to |
| `username` | String | | Unique username |
| `email` | String | | Unique email for the user |
| `first_name` | String | | User's first name |
| `last_name` | String | | User's last name |
| `persona` | Enum | | Role of the user (`teacher`, `student`, `parent`, `admin`) |
| `teacher_profile` | `Teacher` | One-to-One | Teacher-specific profile |
| `student_profile` | `Student` | One-to-One | Student-specific profile |
| `parent_profile` | `Parent` | One-to-One | Parent-specific profile |

---

## Profile & Relationship Models

### `Teacher`
Profile for users with the 'teacher' persona.

| Column | Type | Relationships | Description |
|---|---|---|---|
| `id` | UUID | | Primary Key |
| `user_id` | UUID | One-to-One with `User` | Links to the main user account |
| `school_id` | UUID | Many-to-One with `School` | The school this teacher belongs to |
| `bio` | Text | | A short biography |
| `classes` | `Class` | One-to-Many | Classes taught by this teacher |

### `Student`
Profile for users with the 'student' persona.

| Column | Type | Relationships | Description |
|---|---|---|---|
| `id` | UUID | | Primary Key |
| `user_id` | UUID | One-to-One with `User` | Links to the main user account |
| `school_id` | UUID | Many-to-One with `School` | The school this student belongs to |
| `date_of_birth` | Date | | Student's date of birth |
| `parents` | `Parent` | Many-to-Many via `ParentStudentRelationship` | Parents/guardians of the student |
| `classes` | `Class` | Many-to-Many via `StudentClass` | Classes the student is enrolled in |

### `Parent`
Profile for users with the 'parent' persona.

| Column | Type | Relationships | Description |
|---|---|---|---|
| `id` | UUID | | Primary Key |
| `user_id` | UUID | One-to-One with `User` | Links to the main user account |
| `school_id` | UUID | Many-to-One with `School` | The school this parent belongs to |
| `phone_number` | String | | Parent's contact number |
| `children` | `Student` | Many-to-Many via `ParentStudentRelationship` | Children of this parent |

### `ParentStudentRelationship`
Join table for the many-to-many relationship between parents and students.

| Column | Type | Relationships |
|---|---|---|
| `parent_id` | UUID | Foreign Key to `Parent` |
| `student_id` | UUID | Foreign Key to `Student` |

---

## Academic Structure Models

### `Subject`
Represents an academic subject.

| Column | Type | Relationships | Description |
|---|---|---|---|
| `id` | UUID | | Primary Key |
| `school_id` | UUID | Many-to-One with `School` | The school offering the subject |
| `name` | String | | Name of the subject (e.g., "Mathematics") |
| `description` | Text | | A brief description of the subject |

### `Class`
Represents a specific class section for a subject.

| Column | Type | Relationships | Description |
|---|---|---|---|
| `id` | UUID | | Primary Key |
| `school_id` | UUID | Many-to-One with `School` | The school where the class is held |
| `teacher_id` | UUID | Many-to-One with `Teacher` | The teacher for this class |
| `subject_id` | UUID | Many-to-One with `Subject` | The subject this class is for |
| `room_id` | UUID | Many-to-One with `Room` | The room where the class is held |
| `name` | String | | Name of the class (e.g., "Math 101") |
| `students` | `Student` | Many-to-Many via `StudentClass` | Students enrolled in this class |

### `StudentClass`
Join table for the many-to-many relationship between students and classes.

| Column | Type | Relationships |
|---|---|---|
| `student_id` | UUID | Foreign Key to `Student` |
| `class_id` | UUID | Foreign Key to `Class` |

---
*Note: This schema was generated based on an analysis of the core model files. Other models related to fees, events, assessments, etc., exist but were not included in this summary.*
