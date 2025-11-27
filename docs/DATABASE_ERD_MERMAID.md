# Entity-Relationship Diagram (Mermaid) - Complete

This file contains the complete database Entity-Relationship Diagram (ERD) in Mermaid syntax, based on a full analysis of all models.

```mermaid
erDiagram
    School {
        UUID id PK
        string name
    }

    User {
        UUID id PK
        UUID school_id FK
        string email
        string persona
    }

    Teacher {
        UUID id PK
        UUID user_id FK
    }

    Student {
        UUID id PK
        UUID user_id FK
    }

    Parent {
        UUID id PK
        UUID user_id FK
    }

    ParentStudentRelationship {
        UUID parent_id PK,FK
        UUID student_id PK,FK
    }

    Subject {
        UUID id PK
        UUID school_id FK
        string name
    }

    Room {
        UUID id PK
        UUID school_id FK
        string room_number
    }

    Class {
        UUID id PK
        UUID school_id FK
        UUID subject_id FK
        UUID teacher_id FK
        UUID room_id FK
        string name
    }

    StudentClass {
        UUID student_id PK,FK
        UUID class_id PK,FK
    }

    Lesson {
        UUID id PK
        UUID class_id FK
        UUID teacher_id FK
        string title
    }

    Assessment {
        UUID id PK
        UUID student_id FK
        UUID class_id FK
        UUID teacher_id FK
        string title
    }

    Attendance {
        UUID id PK
        UUID student_id FK
        UUID class_id FK
        date attendance_date
        string status
    }

    Merit {
        UUID id PK
        UUID student_id FK
        UUID awarded_by_id FK
        string category
        int points
    }
    
    Event {
        UUID id PK
        UUID school_id FK
        UUID room_id FK
        UUID organizer_id FK
        string title
    }

    Activity {
        UUID id PK
        UUID school_id FK
        UUID coordinator_id FK
        string name
    }

    ActivityEnrollment {
        UUID activity_id PK,FK
        UUID student_id PK,FK
    }

    Vendor {
        UUID id PK
        UUID school_id FK
        string company_name
    }

    FeeStructure {
        UUID id PK
        UUID school_id FK
        int grade_level
        string academic_year
        numeric yearly_amount
    }

    Bursary {
        UUID id PK
        UUID school_id FK
        string name
        numeric coverage_value
    }
    
    StudentFee {
        UUID id PK
        UUID student_id FK
        UUID bursary_id FK
        string academic_year
        numeric total_amount_due
    }

    Payment {
        UUID id PK
        UUID student_fee_id FK
        numeric amount
        string receipt_number
    }

    ActivityFee {
        UUID id PK
        UUID activity_id FK
        numeric fee_amount
    }

    %% --- Relationships ---

    School ||--o{ User : "has"
    School ||--o{ Teacher : "employs"
    School ||--o{ Student : "enrolls"
    School ||--o{ Parent : "has"
    School ||--o{ Subject : "offers"
    School ||--o{ Room : "has"
    School ||--o{ Class : "holds"
    School ||--o{ Event : "hosts"
    School ||--o{ Activity : "offers"
    School ||--o{ Vendor : "contracts"
    School ||--o{ FeeStructure : "defines"
    School ||--o{ Bursary : "offers"

    User |o--|| Teacher : "profile"
    User |o--|| Student : "profile"
    User |o--|| Parent : "profile"
    User ||--o{ Merit : "awards"
    User ||--o{ Event : "organizes"
    User ||--o{ Activity : "coordinates"

    Parent ||--|{ ParentStudentRelationship : "links to"
    Student ||--|{ ParentStudentRelationship : "links to"

    Student ||--|{ StudentClass : "enrolls in"
    Class ||--|{ StudentClass : "is enrolled by"
    
    Student ||--o{ Assessment : "receives"
    Student ||--o{ Attendance : "records for"
    Student ||--o{ Merit : "earns"
    Student ||--o{ StudentFee : "owes"
    Student ||--o{ ActivityEnrollment : "participates in"

    Teacher ||--o{ Class : "teaches"
    Teacher ||--o{ Lesson : "creates"
    Teacher ||--o{ Assessment : "grades"

    Subject ||--o{ Class : "is basis for"
    
    Class ||--o{ Lesson : "has"
    Class ||--o{ Assessment : "contains"
    Class ||--o{ Attendance : "takes"
    
    Room ||--o{ Class : "hosts"
    Room ||--o{ Event : "hosts"

    Activity ||--|{ ActivityEnrollment : "has"
    Activity ||--o{ ActivityFee : "has fee"
    
    FeeStructure ||--o{ StudentFee : "calculates for"
    Bursary ||--o{ StudentFee : "applies to"
    StudentFee ||--o{ Payment : "is paid by"

```