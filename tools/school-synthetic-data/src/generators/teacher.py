"""
Teacher Generator

Generate teacher profiles linked to user accounts.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
from .base import BaseGenerator


class TeacherGenerator(BaseGenerator):
    """
    Generate teacher profiles

    Responsibilities:
    - Link teacher profiles to users with 'teacher' persona
    - Assign grade levels
    - Set employment details
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate teacher profiles

        Args:
            count: Number of teachers (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated teacher dictionaries
        """
        teachers = []
        school_id = self._get_school_id()

        # Get all teacher users
        teacher_users = [u for u in self.cache.users.values() if u.get("persona") == "teacher"]

        if not teacher_users:
            raise ValueError("No teacher users found in cache. Generate teacher users first.")

        self._log_progress(f"Creating {len(teacher_users)} teacher profiles")

        # Use timestamp to ensure unique employee IDs across runs
        import time
        employee_id_counter = int(time.time() % 100000)

        for user in teacher_users:
            # Assign grade levels (each teacher can teach multiple grades)
            # Some teachers teach all grades (specialists), others specific ranges
            if self.faker.boolean(chance_of_getting_true=30):
                # Specialist (all grades)
                grade_levels = [1, 2, 3, 4, 5, 6, 7]
            else:
                # Specific grade range
                start_grade = self.faker.random_int(min=1, max=5)
                end_grade = min(start_grade + self.faker.random_int(min=1, max=3), 7)
                grade_levels = list(range(start_grade, end_grade + 1))

            # Hire date (within last 10 years)
            hire_date = date.today() - timedelta(days=self.faker.random_int(min=365, max=3650))

            teacher_data = {
                "school_id": school_id,
                "user_id": user["id"],
                "employee_id": f"TCH{employee_id_counter:05d}",
                "hire_date": hire_date.isoformat(),
                "department": self.faker.random_element([
                    "Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"
                ]),
                "job_title": "Teacher",
                "grade_levels": grade_levels,
                "employment_type": self.faker.random_element(["full-time", "part-time"]),
                "status": "active",
                "specializations": self.faker.random_elements(
                    elements=["STEM", "Literacy", "Special Education", "ESL", "Gifted"],
                    length=self.faker.random_int(min=0, max=2),
                    unique=True
                ),
            }

            teacher = self.client.create_teacher(teacher_data)

            # Store with user info for easier lookup
            teacher_with_user = {
                **teacher,
                "user": user,
            }

            self.cache.add_entity("teacher", teacher["id"], teacher_with_user)
            teachers.append(teacher)

            employee_id_counter += 1

        self._log_progress(f"✓ Created {len(teachers)} teacher profiles")

        return teachers
