"""
Class Generator

Generate class records (subject + teacher + grade + room).
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class ClassGenerator(BaseGenerator):
    """
    Generate class records

    Responsibilities:
    - Link Subject, Teacher, Room
    - Distribute across grades
    - Set quarter and academic year
    - Assign class codes
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate class records

        Creates classes for each subject-grade combination with assigned teachers and rooms.

        Args:
            count: Number of classes (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated class dictionaries
        """
        classes = []
        school_id = self._get_school_id()

        # Get entities needed for classes
        subjects = list(self.cache.subjects.values())
        teachers = list(self.cache.teachers.values())
        rooms = [r for r in self.cache.rooms.values() if r["room_type"] == "classroom"]

        if not subjects:
            raise ValueError("No subjects found in cache. Generate subjects first.")
        if not teachers:
            raise ValueError("No teachers found in cache. Generate teachers first.")
        if not rooms:
            raise ValueError("No classroom rooms found in cache. Generate rooms first.")

        # Get dates from config
        dates_config = self.config.get("generation_rules", {}).get("dates", {})
        current_quarter = dates_config.get("current_quarter", "Q2")
        academic_year = "2024-2025"

        grade_levels = [1, 2, 3, 4, 5, 6, 7]

        self._log_progress(f"Creating classes for {len(subjects)} subjects across {len(grade_levels)} grades")

        class_counter = 1

        for grade in grade_levels:
            for subject in subjects:
                # Check if subject is taught at this grade
                if grade not in subject.get("grade_levels", []):
                    continue

                # Assign a teacher (prefer teachers who teach this grade)
                eligible_teachers = [
                    t for t in teachers
                    if grade in t.get("grade_levels", [])
                ]

                if not eligible_teachers:
                    # Fallback to any teacher
                    eligible_teachers = teachers

                teacher = self.faker.random_element(eligible_teachers)

                # Assign a room
                room = self.faker.random_element(rooms)

                class_data = {
                    "school_id": school_id,
                    "subject_id": subject["id"],
                    "teacher_id": teacher["id"],
                    "room_id": room["id"],
                    "code": f"{subject['code']}{grade}{class_counter:02d}",
                    "name": f"Grade {grade} {subject['name']}",
                    "grade_level": grade,
                    "quarter": current_quarter,
                    "academic_year": academic_year,
                    "max_students": self.faker.random_int(min=20, max=28),
                    "current_enrollment": 0,  # Will be updated when students enroll
                    "is_active": True,
                }

                class_obj = self.client.create_class(class_data)

                # Store with related entities for easier access
                class_with_details = {
                    **class_obj,
                    "subject": subject,
                    "teacher": teacher,
                    "room": room,
                }

                self.cache.add_entity("class", class_obj["id"], class_with_details)
                classes.append(class_obj)

                class_counter += 1

        self._log_progress(f"✓ Created {len(classes)} classes")

        return classes
