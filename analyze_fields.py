#!/usr/bin/env python3
"""
Field Analysis Script
Analyzes field consistency across Database, Models, Schemas, and Frontend Types
"""

# Database field definitions (from migrations)
database_fields = {
    "schools": {
        "name": "VARCHAR(255)",
        "slug": "VARCHAR(255)",
        "address_line1": "VARCHAR(255)",
        "address_line2": "VARCHAR(255)",
        "city": "VARCHAR(100)",
        "state": "VARCHAR(100)",
        "postal_code": "VARCHAR(20)",
        "country": "VARCHAR(100)",
        "phone": "VARCHAR(20)",
        "email": "VARCHAR(255)",
        "website_url": "VARCHAR(500)",
        "facebook_url": "VARCHAR(500)",
        "twitter_url": "VARCHAR(500)",
        "instagram_url": "VARCHAR(500)",
        "logo_url": "VARCHAR(500)",
        "timezone": "VARCHAR(50)",
        "locale": "VARCHAR(10)",
        "status": "VARCHAR(20)",
    },
    "users": {
        "email": "VARCHAR(255)",
        "password_hash": "VARCHAR(255)",
        "first_name": "VARCHAR(100)",
        "last_name": "VARCHAR(100)",
        "persona": "VARCHAR(50)",
        "status": "VARCHAR(20)",
        "phone": "VARCHAR(20)",
        "avatar_url": "VARCHAR(500)",
        "keycloak_id": "VARCHAR(255)",
    },
    "teachers": {
        "employee_id": "VARCHAR(50)",
        "department": "VARCHAR(100)",
        "job_title": "VARCHAR(100)",
        "certification_number": "VARCHAR(100)",
        "education_level": "VARCHAR(50)",
        "university": "VARCHAR(200)",
        "employment_type": "VARCHAR(20)",
        "emergency_contact_name": "VARCHAR(200)",
        "emergency_contact_phone": "VARCHAR(20)",
        "emergency_contact_relationship": "VARCHAR(50)",
        "status": "VARCHAR(20)",
        "bio": "TEXT",
        "office_room": "VARCHAR(50)",
    }
}

# Model field definitions (from SQLAlchemy)
model_fields = {
    "schools": {
        "name": "String(255)",
        "slug": "String(255)",
        "address_line1": "String(255)",
        "address_line2": "String(255)",
        "city": "String(100)",
        "state": "String(100)",
        "postal_code": "String(20)",
        "country": "String(100)",
        "phone": "String(20)",
        "email": "String(255)",
        "website_url": "String(500)",
        "facebook_url": "String(500)",
        "twitter_url": "String(500)",
        "instagram_url": "String(500)",
        "logo_url": "String(500)",
        "timezone": "String(50)",
        "locale": "String(10)",
        "status": "String(20)",
    },
    "users": {
        "email": "String(255)",
        "password_hash": "String(255)",
        "first_name": "String(100)",
        "last_name": "String(100)",
        "persona": "String(50)",
        "status": "String(20)",
        "phone": "String(20)",
        "avatar_url": "String(500)",
        "keycloak_id": "String(255)",
    },
    "teachers": {
        "employee_id": "String(50)",
        "department": "String(100)",
        "job_title": "String(100)",
        "certification_number": "String(100)",
        "education_level": "String(50)",
        "university": "String(200)",
        "employment_type": "String(20)",
        "emergency_contact_name": "String(200)",
        "emergency_contact_phone": "String(20)",
        "emergency_contact_relationship": "String(50)",
        "status": "String(20)",
        "bio": "Text",
        "office_room": "String(50)",
    }
}

# Schema field definitions (from Pydantic)
schema_fields = {
    "schools": {
        "name": "max_length=255",
        "slug": "max_length=255",
        "address_line1": "max_length=255",
        "address_line2": "max_length=255",
        "city": "max_length=100",
        "state": "max_length=100",
        "postal_code": "max_length=20",
        "country": "max_length=100",
        "phone": "max_length=20",
        "email": "EmailStr",
        "website_url": "max_length=500",
        "facebook_url": "max_length=500",
        "twitter_url": "max_length=500",
        "instagram_url": "max_length=500",
        "logo_url": "max_length=500",
        "timezone": "max_length=50",
        "locale": "max_length=10",
        "status": "StatusEnum",
    },
    "users": {
        "email": "EmailStr",
        "password": "min_length=8, max_length=100",
        "first_name": "min_length=2, max_length=100",
        "last_name": "min_length=2, max_length=100",
        "persona": "PersonaEnum",
        "status": "StatusEnum",
        "phone": "max_length=20",
        "avatar_url": "max_length=500",
    },
    "teachers": {
        "employee_id": "min_length=1, max_length=50",
        "department": "max_length=100",
        "job_title": "max_length=100",
        "certification_number": "max_length=100",
        "education_level": "EducationLevelEnum",
        "university": "max_length=200",
        "employment_type": "EmploymentTypeEnum",
        "emergency_contact_name": "max_length=200",
        "emergency_contact_phone": "max_length=20",
        "emergency_contact_relationship": "max_length=50",
        "status": "TeacherStatusEnum",
        "bio": "str (no limit)",
        "office_room": "max_length=50",
    }
}

print("=" * 100)
print("FIELD CONSISTENCY ANALYSIS REPORT")
print("=" * 100)
print()

# Check consistency
for table in database_fields:
    print(f"\n{'=' * 100}")
    print(f"TABLE: {table.upper()}")
    print(f"{'=' * 100}")
    print(f"{'Field':<30} {'Database':<20} {'Model':<20} {'Schema':<30} {'Status':<10}")
    print("-" * 100)
    
    all_fields = set(database_fields[table].keys()) | set(model_fields[table].keys()) | set(schema_fields[table].keys())
    
    for field in sorted(all_fields):
        db_val = database_fields[table].get(field, "MISSING")
        model_val = model_fields[table].get(field, "MISSING")
        schema_val = schema_fields[table].get(field, "MISSING")
        
        # Check consistency
        status = "✅ OK"
        if "MISSING" in [db_val, model_val, schema_val]:
            status = "❌ MISSING"
        elif db_val != model_val.replace("String", "VARCHAR").replace("Text", "TEXT"):
            status = "⚠️ MISMATCH"
        
        print(f"{field:<30} {db_val:<20} {model_val:<20} {schema_val:<30} {status:<10}")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print("✅ OK       - Field is consistent across all layers")
print("⚠️ MISMATCH - Field lengths differ between layers")
print("❌ MISSING  - Field is missing in one or more layers")
print()
