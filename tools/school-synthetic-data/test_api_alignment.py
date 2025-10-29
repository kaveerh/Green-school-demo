#!/usr/bin/env python3
"""
Test API Alignment

Test each feature's Create and Delete operations against the actual API.
"""
import requests
import json
import sys
import uuid
from datetime import date, datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
SCHOOL_ID = None
CREATED_IDS = {}


def unique_email(prefix: str) -> str:
    """Generate unique email"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.com"


def log(msg: str):
    print(f"[TEST] {msg}")


def create_school() -> str:
    """Get existing test school ID"""
    global SCHOOL_ID
    
    log("Getting existing school...")
    resp = requests.get(f"{BASE_URL}/api/v1/schools")
    resp.raise_for_status()
    schools = resp.json()["data"]
    
    if not schools:
        raise Exception("No schools found. Please create a school first.")
    
    SCHOOL_ID = schools[0]["id"]
    log(f"✓ Using school: {SCHOOL_ID}")
    return SCHOOL_ID


def delete_school(school_id: str):
    """Skip deleting school - using existing"""
    log(f"Skipping school deletion (using existing school)")


def test_users():
    """Test Users feature"""
    log("\n=== Testing USERS ===")
    
    # Create
    data = {
        "school_id": SCHOOL_ID,
        "email": unique_email("testuser"),
        "first_name": "Test",
        "last_name": "User",
        "persona": "teacher",
        "status": "active"
    }
    
    log("Creating user...")
    resp = requests.post(f"{BASE_URL}/api/v1/users", json=data)
    if resp.status_code != 201:
        log(f"✗ Failed: {resp.status_code} - {resp.text}")
        return False
    
    user = resp.json()
    user_id = user["id"]
    CREATED_IDS["user"] = user_id
    log(f"✓ User created: {user_id}")
    
    # Delete
    log(f"Deleting user {user_id}...")
    resp = requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
    if resp.status_code not in [200, 204]:
        log(f"✗ Delete failed: {resp.status_code} - {resp.text}")
        return False
    
    log("✓ User deleted")
    return True


def test_teachers():
    """Test Teachers feature"""
    log("\n=== Testing TEACHERS ===")
    
    # Create user first
    user_data = {
        "school_id": SCHOOL_ID,
        "email": unique_email("teacher"),
        "first_name": "Teacher",
        "last_name": "Test",
        "persona": "teacher",
        "status": "active"
    }
    resp = requests.post(f"{BASE_URL}/api/v1/users", json=user_data)
    resp.raise_for_status()
    user = resp.json()
    user_id = user["id"]
    
    # Create teacher
    data = {
        "school_id": SCHOOL_ID,
        "user_id": user_id,
        "employee_id": "T001",
        "hire_date": str(date.today()),
        "status": "active"
    }
    
    log("Creating teacher...")
    resp = requests.post(f"{BASE_URL}/api/v1/teachers", json=data)
    if resp.status_code != 201:
        log(f"✗ Failed: {resp.status_code} - {resp.text}")
        requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
        return False
    
    teacher = resp.json()
    teacher_id = teacher["id"]
    CREATED_IDS["teacher"] = teacher_id
    log(f"✓ Teacher created: {teacher_id}")
    
    # Delete
    log(f"Deleting teacher {teacher_id}...")
    resp = requests.delete(f"{BASE_URL}/api/v1/teachers/{teacher_id}")
    if resp.status_code not in [200, 204]:
        log(f"✗ Delete failed: {resp.status_code} - {resp.text}")
        requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
        return False
    
    log("✓ Teacher deleted")
    requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
    return True


def test_students():
    """Test Students feature"""
    log("\n=== Testing STUDENTS ===")
    
    # Create user first
    user_data = {
        "school_id": SCHOOL_ID,
        "email": unique_email("student"),
        "first_name": "Student",
        "last_name": "Test",
        "persona": "student",
        "status": "active"
    }
    resp = requests.post(f"{BASE_URL}/api/v1/users", json=user_data)
    resp.raise_for_status()
    user = resp.json()
    user_id = user["id"]
    
    # Create student
    student_id_num = uuid.uuid4().hex[:8].upper()
    data = {
        "school_id": SCHOOL_ID,
        "user_id": user_id,
        "student_id": f"S{student_id_num}",
        "grade_level": 5,
        "date_of_birth": "2015-01-15",
        "enrollment_date": str(date.today()),
        "status": "enrolled"
    }
    
    log("Creating student...")
    resp = requests.post(f"{BASE_URL}/api/v1/students", json=data)
    if resp.status_code != 201:
        log(f"✗ Failed: {resp.status_code} - {resp.text}")
        requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
        return False
    
    student = resp.json()
    student_id = student["id"]
    CREATED_IDS["student"] = student_id
    log(f"✓ Student created: {student_id}")
    
    # Delete
    log(f"Deleting student {student_id}...")
    resp = requests.delete(f"{BASE_URL}/api/v1/students/{student_id}")
    if resp.status_code not in [200, 204]:
        log(f"✗ Delete failed: {resp.status_code} - {resp.text}")
        requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
        return False
    
    log("✓ Student deleted")
    requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
    return True


def test_parents():
    """Test Parents feature"""
    log("\n=== Testing PARENTS ===")
    
    # Create user first
    user_data = {
        "school_id": SCHOOL_ID,
        "email": unique_email("parent"),
        "first_name": "Parent",
        "last_name": "Test",
        "persona": "parent",
        "status": "active"
    }
    resp = requests.post(f"{BASE_URL}/api/v1/users", json=user_data)
    resp.raise_for_status()
    user = resp.json()
    user_id = user["id"]
    
    # Create parent
    data = {
        "school_id": SCHOOL_ID,
        "user_id": user_id,
        "relationship_type": "mother",
        "is_primary_contact": True,
        "is_emergency_contact": True
    }
    
    log("Creating parent...")
    resp = requests.post(f"{BASE_URL}/api/v1/parents", json=data)
    if resp.status_code != 201:
        log(f"✗ Failed: {resp.status_code} - {resp.text}")
        requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
        return False
    
    parent = resp.json()
    parent_id = parent["id"]
    CREATED_IDS["parent"] = parent_id
    log(f"✓ Parent created: {parent_id}")
    
    # Delete
    log(f"Deleting parent {parent_id}...")
    resp = requests.delete(f"{BASE_URL}/api/v1/parents/{parent_id}")
    if resp.status_code not in [200, 204]:
        log(f"✗ Delete failed: {resp.status_code} - {resp.text}")
        requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
        return False
    
    log("✓ Parent deleted")
    requests.delete(f"{BASE_URL}/api/v1/users/{user_id}")
    return True


def test_subjects():
    """Test Subjects feature"""
    log("\n=== Testing SUBJECTS ===")
    
    code = f"MATH_{uuid.uuid4().hex[:6].upper()}"
    data = {
        "school_id": SCHOOL_ID,
        "name": f"Test Math {code}",
        "code": code,
        "grade_levels": [5, 6, 7],
        "status": "active"
    }
    
    log("Creating subject...")
    resp = requests.post(f"{BASE_URL}/api/v1/subjects", json=data)
    if resp.status_code != 201:
        log(f"✗ Failed: {resp.status_code} - {resp.text}")
        return False
    
    subject = resp.json()
    subject_id = subject["id"]
    CREATED_IDS["subject"] = subject_id
    log(f"✓ Subject created: {subject_id}")
    
    # Delete
    log(f"Deleting subject {subject_id}...")
    resp = requests.delete(f"{BASE_URL}/api/v1/subjects/{subject_id}")
    if resp.status_code not in [200, 204]:
        log(f"✗ Delete failed: {resp.status_code} - {resp.text}")
        return False
    
    log("✓ Subject deleted")
    return True


def test_rooms():
    """Test Rooms feature"""
    log("\n=== Testing ROOMS ===")
    
    room_num = f"TEST{uuid.uuid4().hex[:6].upper()}"
    data = {
        "school_id": SCHOOL_ID,
        "name": f"Test Room {room_num}",
        "room_number": room_num,
        "room_type": "classroom",
        "capacity": 30,
        "status": "active"
    }
    
    log("Creating room...")
    resp = requests.post(f"{BASE_URL}/api/v1/rooms", json=data)
    if resp.status_code != 201:
        log(f"✗ Failed: {resp.status_code} - {resp.text}")
        return False
    
    room = resp.json()
    room_id = room["id"]
    CREATED_IDS["room"] = room_id
    log(f"✓ Room created: {room_id}")
    
    # Delete
    log(f"Deleting room {room_id}...")
    resp = requests.delete(f"{BASE_URL}/api/v1/rooms/{room_id}")
    if resp.status_code not in [200, 204]:
        log(f"✗ Delete failed: {resp.status_code} - {resp.text}")
        return False
    
    log("✓ Room deleted")
    return True


def main():
    """Run all tests"""
    try:
        # Create school
        create_school()
        
        # Test each feature
        results = {
            "users": test_users(),
            "teachers": test_teachers(),
            "students": test_students(),
            "parents": test_parents(),
            "subjects": test_subjects(),
            "rooms": test_rooms(),
        }
        
        # Cleanup
        delete_school(SCHOOL_ID)
        
        # Summary
        log("\n=== SUMMARY ===")
        for feature, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            log(f"{feature}: {status}")
        
        all_passed = all(results.values())
        if all_passed:
            log("\n✓ All tests passed!")
            sys.exit(0)
        else:
            log("\n✗ Some tests failed")
            sys.exit(1)
            
    except Exception as e:
        log(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
