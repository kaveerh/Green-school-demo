"""
Student Generator

Generate student profiles linked to user accounts.
"""
from typing import List, Dict, Any
from datetime import date
from .base import BaseGenerator


class StudentGenerator(BaseGenerator):
    """
    Generate student profiles

    Responsibilities:
    - Link student profiles to users with 'student' persona
    - Distribute across grade levels
    - Assign student IDs
    - Set enrollment details
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate student profiles

        Args:
            count: Number of students (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated student dictionaries
        """
        students = []
        school_id = self._get_school_id()

        # Get all student users
        student_users = [u for u in self.cache.users.values() if u.get("persona") == "student"]

        if not student_users:
            raise ValueError("No student users found in cache. Generate student users first.")

        # Get grade distribution from config
        grade_dist = self.config.get("generation_rules", {}).get("grade_distribution", {})

        # Convert to list of (grade, count) tuples
        grade_assignments = []
        for grade, count in grade_dist.items():
            grade_assignments.extend([int(grade)] * count)

        if len(grade_assignments) != len(student_users):
            raise ValueError(
                f"Grade distribution ({len(grade_assignments)}) doesn't match student count ({len(student_users)})"
            )

        self._log_progress(f"Creating {len(student_users)} student profiles")

        student_id_counter = 1001
        academic_year_start = self.config.get("generation_rules", {}).get("dates", {}).get("academic_year_start", "2024-09-01")

        for i, user in enumerate(student_users):
            grade = grade_assignments[i]

            # Calculate age based on grade (typically grade + 5 years old)
            typical_age = grade + 5
            birth_year = date.today().year - typical_age

            # Random birth date within that year
            date_of_birth = self.faker.date_of_birth(
                minimum_age=typical_age,
                maximum_age=typical_age + 2
            )

            student_data = {
                "school_id": school_id,
                "user_id": user["id"],
                "student_id": f"STU{student_id_counter:05d}",
                "grade_level": grade,
                "date_of_birth": date_of_birth.isoformat(),
                "gender": self.faker.random_element(["male", "female", "other"]),
                "enrollment_date": academic_year_start,
                "status": "enrolled",
                "allergies": self.faker.random_elements(
                    elements=["Peanuts", "Tree nuts", "Milk", "Eggs", "Wheat", "Soy", "Fish", "Shellfish"],
                    length=self.faker.random_int(min=0, max=2),
                    unique=True
                ) if self.faker.boolean(chance_of_getting_true=20) else [],
                "medical_notes": self.faker.text(max_nb_chars=100) if self.faker.boolean(chance_of_getting_true=10) else None,
            }

            student = self.client.create_student(student_data)

            # Store with user info for easier lookup
            student_with_user = {
                **student,
                "user": user,
                "first_name": user["first_name"],
                "last_name": user["last_name"],
            }

            self.cache.add_entity("student", student["id"], student_with_user)
            students.append(student)

            student_id_counter += 1

        self._log_progress(f"✓ Created {len(students)} student profiles")

        return students
