"""
Assessment Generator

Generate assessments (tests, quizzes, projects) for students.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
import random
from .base import BaseGenerator


class AssessmentGenerator(BaseGenerator):
    """
    Generate assessment records

    Responsibilities:
    - Create assessments for each student
    - Distribute assessment types (test, quiz, project, etc.)
    - Assign realistic grades
    - Set quarters
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate assessment records

        Creates multiple assessments per student across different subjects.

        Args:
            count: Assessments per student (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated assessment dictionaries
        """
        assessments = []
        school_id = self._get_school_id()

        # Get assessments per student from config
        assessments_per_student = self.config.get("data_volumes", {}).get("assessments_per_student", 20)

        # Get students
        students = list(self.cache.students.values())

        if not students:
            raise ValueError("No students found in cache. Generate students first.")

        # Get assessment type distribution
        assessment_types = self.config.get("generation_rules", {}).get("assessment_types", {})
        grading_config = self.config.get("generation_rules", {}).get("grading", {})
        grade_weights = self.config.get("generation_rules", {}).get("grade_distribution_weights", {})

        # Get date range
        dates_config = self.config.get("generation_rules", {}).get("dates", {})
        start_date_str = dates_config.get("academic_year_start", "2024-09-01")

        start_date = date.fromisoformat(start_date_str)

        total_assessments = len(students) * assessments_per_student
        self._log_progress(f"Creating {total_assessments} assessments ({assessments_per_student} per student)")

        quarters = ["Q1", "Q2", "Q3", "Q4"]

        for student in students:
            grade_level = student.get("grade_level")

            # Get student's enrolled classes from cache
            student_enrollments = [
                e for e in self.cache.student_classes
                if e.get("student_id") == student["id"]
            ]

            if not student_enrollments:
                self._log_progress(f"⚠ No class enrollments for student {student.get('student_id')}")
                continue

            # Get classes
            student_class_ids = [e.get("class_id") for e in student_enrollments]
            student_classes = [
                c for c in self.cache.classes.values()
                if c.get("id") in student_class_ids
            ]

            if not student_classes:
                continue

            # Create assessments for this student
            for i in range(assessments_per_student):
                # Pick a random class
                class_obj = random.choice(student_classes)
                subject = class_obj.get("subject", {})
                teacher = class_obj.get("teacher", {})

                # Pick assessment type based on distribution
                assessment_type = random.choices(
                    population=list(assessment_types.keys()),
                    weights=list(assessment_types.values()),
                    k=1
                )[0]

                # Pick quarter
                quarter = random.choice(quarters)

                # Generate assessment date
                days_offset = random.randint(0, 270)  # Spread over school year
                assessment_date = start_date + timedelta(days=days_offset)

                # Generate grade (weighted distribution)
                grade_category = random.choices(
                    population=list(grade_weights.keys()),
                    weights=list(grade_weights.values()),
                    k=1
                )[0]

                # Get percentage range for this category
                grade_range = grading_config.get(grade_category, [70, 100])
                percentage = random.uniform(grade_range[0], grade_range[1])

                # Total points
                total_points = random.choice([50, 100]) if assessment_type != "exam" else random.choice([100, 150, 200])

                # Calculate points earned
                points_earned = round((percentage / 100) * total_points, 2)

                # Assign letter grade
                letter_grade = self._calculate_letter_grade(percentage)

                # Status
                status = random.choices(
                    population=["graded", "pending", "submitted"],
                    weights=[0.7, 0.2, 0.1],
                    k=1
                )[0]

                assessment_data = {
                    "school_id": school_id,
                    "student_id": student["id"],
                    "class_id": class_obj["id"],
                    "subject_id": subject["id"],
                    "teacher_id": teacher["id"],
                    "title": f"{subject.get('name', 'Subject')} {assessment_type.title()} {i + 1}",
                    "description": f"{assessment_type.title()} for {subject.get('name', 'Subject')} - Grade {grade_level}",
                    "assessment_type": assessment_type,
                    "quarter": quarter,
                    "assessment_date": assessment_date.isoformat(),
                    "due_date": assessment_date.isoformat(),
                    "total_points": total_points,
                    "points_earned": points_earned if status == "graded" else None,
                    "percentage": percentage if status == "graded" else None,
                    "letter_grade": letter_grade if status == "graded" else None,
                    "status": status,
                    "weight": 1.0 if assessment_type != "exam" else 2.0,
                    "is_extra_credit": random.random() < 0.05,  # 5% extra credit
                }

                if status == "graded" and random.random() < 0.6:  # 60% have feedback
                    assessment_data["feedback"] = self.faker.sentence(nb_words=10)

                assessment = self.client.create_assessment(assessment_data)
                self.cache.add_entity("assessment", assessment["id"], assessment)
                assessments.append(assessment)

        self._log_progress(f"✓ Created {len(assessments)} assessments")

        return assessments

    def _calculate_letter_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage"""
        if percentage >= 97:
            return "A+"
        elif percentage >= 93:
            return "A"
        elif percentage >= 90:
            return "A-"
        elif percentage >= 87:
            return "B+"
        elif percentage >= 83:
            return "B"
        elif percentage >= 80:
            return "B-"
        elif percentage >= 77:
            return "C+"
        elif percentage >= 73:
            return "C"
        elif percentage >= 70:
            return "C-"
        elif percentage >= 67:
            return "D+"
        elif percentage >= 63:
            return "D"
        elif percentage >= 60:
            return "D-"
        else:
            return "F"
