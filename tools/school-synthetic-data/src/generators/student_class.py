"""
Student-Class Enrollment Generator

Enroll students in classes based on their grade level.
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class StudentClassGenerator(BaseGenerator):
    """
    Generate student-class enrollments

    Responsibilities:
    - Enroll each student in classes for their grade
    - Ensure students are in all required subject classes
    - Track enrollment dates
    """

    def generate(self, count: int = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate student-class enrollments

        Each student gets enrolled in classes matching their grade level.

        Args:
            count: Not used (enrollments based on students and classes)
            **kwargs: Additional parameters

        Returns:
            List of generated enrollment dictionaries
        """
        enrollments = []

        # Get students and classes
        students = list(self.cache.students.values())
        all_classes = list(self.cache.classes.values())

        if not students:
            raise ValueError("No students found in cache. Generate students first.")
        if not all_classes:
            raise ValueError("No classes found in cache. Generate classes first.")

        # Get enrollment date from config
        dates_config = self.config.get("generation_rules", {}).get("dates", {})
        enrollment_date = dates_config.get("academic_year_start", "2024-09-01")

        self._log_progress(f"Enrolling {len(students)} students in classes")

        total_enrollments = 0

        for student in students:
            grade = student.get("grade_level")

            # Find all classes for this student's grade
            grade_classes = [
                c for c in all_classes
                if c.get("grade_level") == grade
            ]

            if not grade_classes:
                self._log_progress(f"⚠ No classes found for grade {grade}")
                continue

            # Enroll student in each class for their grade
            for class_obj in grade_classes:
                enrollment_data = {
                    "student_id": student["id"],
                    "enrollment_date": enrollment_date,
                    "status": "enrolled",
                }

                try:
                    enrollment = self.client.enroll_student_in_class(
                        class_obj["id"],
                        enrollment_data
                    )

                    # Track in cache
                    self.cache.add_student_class_enrollment(
                        student["id"],
                        class_obj["id"],
                        enrollment_date
                    )

                    enrollments.append(enrollment)
                    total_enrollments += 1

                except Exception as e:
                    self._log_progress(f"⚠ Error enrolling student {student['student_id']} in class {class_obj['code']}: {e}")

        self._log_progress(f"✓ Created {total_enrollments} student-class enrollments")

        return enrollments
