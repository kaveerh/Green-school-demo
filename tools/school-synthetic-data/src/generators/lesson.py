"""
Lesson Generator

Generate lesson plans for classes.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
from .base import BaseGenerator


class LessonGenerator(BaseGenerator):
    """
    Generate lesson records

    Responsibilities:
    - Create lessons for each class
    - Schedule lessons throughout academic year
    - Set learning objectives and materials
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate lesson records

        Creates multiple lessons per class throughout the academic year.

        Args:
            count: Lessons per class (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated lesson dictionaries
        """
        lessons = []
        school_id = self._get_school_id()

        # Get lessons per class from config
        lessons_per_class = self.config.get("data_volumes", {}).get("lessons_per_class", 30)

        # Get all classes
        all_classes = list(self.cache.classes.values())

        if not all_classes:
            raise ValueError("No classes found in cache. Generate classes first.")

        # Get date range from config
        dates_config = self.config.get("generation_rules", {}).get("dates", {})
        start_date_str = dates_config.get("academic_year_start", "2024-09-01")
        end_date_str = dates_config.get("academic_year_end", "2025-06-30")

        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)

        total_lessons = len(all_classes) * lessons_per_class
        self._log_progress(f"Creating {total_lessons} lessons ({lessons_per_class} per class)")

        lesson_counter = 1

        for class_obj in all_classes:
            subject = class_obj.get("subject", {})
            teacher = class_obj.get("teacher", {})

            # Distribute lessons across the academic year
            # Skip weekends (school days only)
            current_date = start_date
            lessons_created = 0

            while lessons_created < lessons_per_class and current_date <= end_date:
                # Skip weekends
                if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    current_date += timedelta(days=1)
                    continue

                # Generate lesson
                lesson_topics = [
                    "Introduction", "Basic Concepts", "Practice Problems", "Review",
                    "Advanced Topics", "Group Work", "Assessment Prep", "Project Work",
                    "Discussion", "Lab Activity", "Reading Comprehension", "Writing Exercise"
                ]

                topic = self.faker.random_element(lesson_topics)

                lesson_data = {
                    "school_id": school_id,
                    "class_id": class_obj["id"],
                    "teacher_id": teacher["id"],
                    "subject_id": subject["id"],
                    "title": f"{subject.get('name', 'Subject')} - {topic} (Lesson {lesson_counter})",
                    "lesson_number": lessons_created + 1,
                    "scheduled_date": current_date.isoformat(),
                    "duration_minutes": self.faker.random_element([45, 50, 60, 90]),
                    "description": f"Lesson on {topic} for Grade {class_obj.get('grade_level', 1)} {subject.get('name', 'Subject')}",
                    "learning_objectives": [
                        f"Understand {topic.lower()} concepts",
                        f"Apply {topic.lower()} skills",
                        f"Demonstrate mastery of {topic.lower()}"
                    ][:self.faker.random_int(min=2, max=3)],
                    "materials_needed": self.faker.random_elements(
                        elements=["Textbook", "Workbook", "Notebook", "Pencils", "Calculator", "Handouts", "Computer"],
                        length=self.faker.random_int(min=2, max=4),
                        unique=True
                    ),
                    "status": self.faker.random_element(
                        elements=["completed", "scheduled", "in_progress"],
                        probabilities=[0.6, 0.3, 0.1]
                    ),
                    "color": subject.get("color", "#757575"),
                }

                lesson = self.client.create_lesson(lesson_data)
                self.cache.add_entity("lesson", lesson["id"], lesson)
                lessons.append(lesson)

                lessons_created += 1
                lesson_counter += 1

                # Move to next school day (skip some days for variety)
                current_date += timedelta(days=self.faker.random_int(min=1, max=3))

        self._log_progress(f"✓ Created {len(lessons)} lessons")

        return lessons
