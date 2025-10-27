"""
Entity Cache System

Tracks all generated entity UUIDs and supports name-based lookups.
"""
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import random


@dataclass
class EntityCache:
    """
    Central cache for all generated entity UUIDs

    Supports:
    - UUID storage by entity type
    - Lookup by name/email/student_id
    - Relationship tracking
    - Export/import for persistence
    """

    schools: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    users: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    teachers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    parents: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    students: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    subjects: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    rooms: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    classes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    lessons: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    assessments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    attendance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    events: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    activities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    vendors: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    merits: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Relationship tracking
    parent_students: List[Dict[str, str]] = field(default_factory=list)
    student_classes: List[Dict[str, str]] = field(default_factory=list)

    def add_entity(self, entity_type: str, uuid: str, data: Dict[str, Any]) -> None:
        """
        Store entity with UUID

        Args:
            entity_type: Type of entity (school, user, teacher, etc.)
            uuid: Entity UUID
            data: Entity data dictionary
        """
        cache_map = {
            "school": self.schools,
            "user": self.users,
            "teacher": self.teachers,
            "parent": self.parents,
            "student": self.students,
            "subject": self.subjects,
            "room": self.rooms,
            "class": self.classes,
            "lesson": self.lessons,
            "assessment": self.assessments,
            "attendance": self.attendance,
            "event": self.events,
            "activity": self.activities,
            "vendor": self.vendors,
            "merit": self.merits,
        }

        if entity_type in cache_map:
            cache_map[entity_type][uuid] = data
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")

    def find_user_by_name(
        self, first_name: str, last_name: str
    ) -> Optional[Dict[str, Any]]:
        """Find user by name"""
        for user in self.users.values():
            if (
                user.get("first_name", "").lower() == first_name.lower()
                and user.get("last_name", "").lower() == last_name.lower()
            ):
                return user
        return None

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        for user in self.users.values():
            if user.get("email", "").lower() == email.lower():
                return user
        return None

    def find_student_by_student_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Find student by student ID"""
        for student in self.students.values():
            if student.get("student_id") == student_id:
                return student
        return None

    def find_teacher_by_name(
        self, first_name: str, last_name: str
    ) -> Optional[Dict[str, Any]]:
        """Find teacher by user name"""
        for teacher in self.teachers.values():
            user_data = teacher.get("user", {})
            if (
                user_data.get("first_name", "").lower() == first_name.lower()
                and user_data.get("last_name", "").lower() == last_name.lower()
            ):
                return teacher
        return None

    def find_parent_by_name(
        self, first_name: str, last_name: str
    ) -> Optional[Dict[str, Any]]:
        """Find parent by user name"""
        for parent in self.parents.values():
            user_data = parent.get("user", {})
            if (
                user_data.get("first_name", "").lower() == first_name.lower()
                and user_data.get("last_name", "").lower() == last_name.lower()
            ):
                return parent
        return None

    def get_random_entities(
        self, entity_type: str, count: int = 1
    ) -> List[Dict[str, Any]]:
        """Get random entities of a type"""
        cache_map = {
            "school": self.schools,
            "user": self.users,
            "teacher": self.teachers,
            "parent": self.parents,
            "student": self.students,
            "subject": self.subjects,
            "room": self.rooms,
            "class": self.classes,
            "lesson": self.lessons,
            "assessment": self.assessments,
            "attendance": self.attendance,
            "event": self.events,
            "activity": self.activities,
            "vendor": self.vendors,
            "merit": self.merits,
        }

        if entity_type not in cache_map:
            raise ValueError(f"Unknown entity type: {entity_type}")

        entities = list(cache_map[entity_type].values())

        if not entities:
            return []

        if count >= len(entities):
            return entities

        return random.sample(entities, count)

    def get_all_entities(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get all entities of a type"""
        cache_map = {
            "school": self.schools,
            "user": self.users,
            "teacher": self.teachers,
            "parent": self.parents,
            "student": self.students,
            "subject": self.subjects,
            "room": self.rooms,
            "class": self.classes,
            "lesson": self.lessons,
            "assessment": self.assessments,
            "attendance": self.attendance,
            "event": self.events,
            "activity": self.activities,
            "vendor": self.vendors,
            "merit": self.merits,
        }

        if entity_type not in cache_map:
            raise ValueError(f"Unknown entity type: {entity_type}")

        return list(cache_map[entity_type].values())

    def get_entity_count(self, entity_type: str) -> int:
        """Get count of entities of a type"""
        return len(self.get_all_entities(entity_type))

    def add_parent_student_relationship(
        self, parent_id: str, student_id: str, relationship_type: str
    ) -> None:
        """Track parent-student relationship"""
        self.parent_students.append(
            {
                "parent_id": parent_id,
                "student_id": student_id,
                "relationship_type": relationship_type,
            }
        )

    def add_student_class_enrollment(
        self, student_id: str, class_id: str, enrollment_date: str
    ) -> None:
        """Track student-class enrollment"""
        self.student_classes.append(
            {
                "student_id": student_id,
                "class_id": class_id,
                "enrollment_date": enrollment_date,
            }
        )

    def export_to_json(self, filepath: str) -> None:
        """Export cache to JSON file"""
        data = {
            "schools": self.schools,
            "users": self.users,
            "teachers": self.teachers,
            "parents": self.parents,
            "students": self.students,
            "subjects": self.subjects,
            "rooms": self.rooms,
            "classes": self.classes,
            "lessons": self.lessons,
            "assessments": self.assessments,
            "attendance": self.attendance,
            "events": self.events,
            "activities": self.activities,
            "vendors": self.vendors,
            "merits": self.merits,
            "parent_students": self.parent_students,
            "student_classes": self.student_classes,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_from_json(self, filepath: str) -> None:
        """Import cache from JSON file"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.schools = data.get("schools", {})
        self.users = data.get("users", {})
        self.teachers = data.get("teachers", {})
        self.parents = data.get("parents", {})
        self.students = data.get("students", {})
        self.subjects = data.get("subjects", {})
        self.rooms = data.get("rooms", {})
        self.classes = data.get("classes", {})
        self.lessons = data.get("lessons", {})
        self.assessments = data.get("assessments", {})
        self.attendance = data.get("attendance", {})
        self.events = data.get("events", {})
        self.activities = data.get("activities", {})
        self.vendors = data.get("vendors", {})
        self.merits = data.get("merits", {})
        self.parent_students = data.get("parent_students", [])
        self.student_classes = data.get("student_classes", [])

    def get_statistics(self) -> Dict[str, int]:
        """Get entity count statistics"""
        return {
            "schools": len(self.schools),
            "users": len(self.users),
            "teachers": len(self.teachers),
            "parents": len(self.parents),
            "students": len(self.students),
            "subjects": len(self.subjects),
            "rooms": len(self.rooms),
            "classes": len(self.classes),
            "lessons": len(self.lessons),
            "assessments": len(self.assessments),
            "attendance": len(self.attendance),
            "events": len(self.events),
            "activities": len(self.activities),
            "vendors": len(self.vendors),
            "merits": len(self.merits),
            "parent_student_relationships": len(self.parent_students),
            "student_class_enrollments": len(self.student_classes),
        }

    def clear(self) -> None:
        """Clear all cached data"""
        self.schools.clear()
        self.users.clear()
        self.teachers.clear()
        self.parents.clear()
        self.students.clear()
        self.subjects.clear()
        self.rooms.clear()
        self.classes.clear()
        self.lessons.clear()
        self.assessments.clear()
        self.attendance.clear()
        self.events.clear()
        self.activities.clear()
        self.vendors.clear()
        self.merits.clear()
        self.parent_students.clear()
        self.student_classes.clear()
