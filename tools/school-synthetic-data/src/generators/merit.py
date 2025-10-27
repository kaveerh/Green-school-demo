"""
Merit Generator

Generate student merit/award records.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
import random
from .base import BaseGenerator


class MeritGenerator(BaseGenerator):
    """
    Generate merit records

    Responsibilities:
    - Create merit awards for students
    - Distribute across categories
    - Assign points and quarters
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate merit records

        Args:
            count: Merits per student (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated merit dictionaries
        """
        merits = []
        school_id = self._get_school_id()

        # Get merits per student from config
        merits_per_student = self.config.get("data_volumes", {}).get("merits_per_student", 5)

        # Get students
        students = list(self.cache.students.values())

        if not students:
            raise ValueError("No students found in cache. Generate students first.")

        # Get teachers for awarded_by
        teachers = list(self.cache.teachers.values())

        if not teachers:
            raise ValueError("No teachers found in cache. Generate teachers first.")

        # Get merit configuration
        merit_categories = self.config.get("generation_rules", {}).get("merit_categories", {})
        merit_points_config = self.config.get("generation_rules", {}).get("merit_points", {})

        # Get date range
        dates_config = self.config.get("generation_rules", {}).get("dates", {})
        start_date_str = dates_config.get("academic_year_start", "2024-09-01")
        start_date = date.fromisoformat(start_date_str)

        total_merits = len(students) * merits_per_student
        self._log_progress(f"Creating {total_merits} merits ({merits_per_student} per student)")

        quarters = ["Q1", "Q2", "Q3", "Q4"]

        for student in students:
            for i in range(merits_per_student):
                # Pick category based on distribution
                category = random.choices(
                    population=list(merit_categories.keys()),
                    weights=list(merit_categories.values()),
                    k=1
                )[0]

                # Pick points tier
                tier = random.choice(list(merit_points_config.keys()))
                points_range = merit_points_config[tier]
                points = random.randint(points_range[0], points_range[1])

                # Pick quarter
                quarter = random.choice(quarters)

                # Generate date
                days_offset = random.randint(0, 270)
                merit_date = start_date + timedelta(days=days_offset)

                # Pick teacher who awarded it
                awarded_by = random.choice(teachers)

                # Generate reason based on category
                if category == "academic":
                    reason = random.choice([
                        "Excellent test performance",
                        "Outstanding homework completion",
                        "Significant improvement in grades",
                        "Perfect attendance to study group",
                        "Excellent project presentation"
                    ])
                elif category == "behavior":
                    reason = random.choice([
                        "Respectful and kind to peers",
                        "Following classroom rules",
                        "Helping other students",
                        "Positive attitude",
                        "Good citizenship"
                    ])
                elif category == "participation":
                    reason = random.choice([
                        "Active class participation",
                        "Volunteering for activities",
                        "Contributing to group work",
                        "Asking thoughtful questions",
                        "Engaging in discussions"
                    ])
                elif category == "leadership":
                    reason = random.choice([
                        "Leading group project",
                        "Mentoring younger students",
                        "Taking initiative",
                        "Demonstrating responsibility",
                        "Setting good example"
                    ])
                elif category == "attendance":
                    reason = random.choice([
                        "Perfect attendance this month",
                        "Never tardy",
                        "Consistent punctuality",
                        "100% attendance this quarter",
                        "Always prepared for class"
                    ])
                else:
                    reason = f"Outstanding {category}"

                merit_data = {
                    "school_id": school_id,
                    "student_id": student["id"],
                    "awarded_by_id": awarded_by["user"]["id"],
                    "category": category,
                    "points": points,
                    "reason": reason,
                    "quarter": quarter,
                    "awarded_date": merit_date.isoformat(),
                    "is_class_award": random.random() < 0.1,  # 10% are class awards
                }

                merit = self.client.create_merit(merit_data)
                self.cache.add_entity("merit", merit["id"], merit)
                merits.append(merit)

        self._log_progress(f"✓ Created {len(merits)} merits")

        return merits
