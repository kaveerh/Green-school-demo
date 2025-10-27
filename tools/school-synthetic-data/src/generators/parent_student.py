"""
Parent-Student Relationship Generator

Link parents to students (1 parent per student as specified).
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class ParentStudentGenerator(BaseGenerator):
    """
    Generate parent-student relationships

    Responsibilities:
    - Link each student to exactly 1 parent
    - Set relationship type (mother, father, guardian)
    - Configure permissions
    """

    def generate(self, count: int = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate parent-student relationships

        Each student gets exactly 1 parent as specified.

        Args:
            count: Not used (one relationship per student)
            **kwargs: Additional parameters

        Returns:
            List of generated relationship dictionaries
        """
        relationships = []
        school_id = self._get_school_id()

        # Get all students and parents
        students = list(self.cache.students.values())
        parents = list(self.cache.parents.values())

        if not students:
            raise ValueError("No students found in cache. Generate students first.")

        if not parents:
            raise ValueError("No parents found in cache. Generate parents first.")

        if len(parents) < len(students):
            raise ValueError(
                f"Not enough parents ({len(parents)}) for students ({len(students)}). "
                f"Each student needs 1 parent."
            )

        self._log_progress(f"Creating {len(students)} parent-student relationships")

        # Assign 1 parent to each student
        for i, student in enumerate(students):
            parent = parents[i]

            relationship_type = self.faker.random_element([
                "mother",
                "father",
                "guardian",
                "stepmother",
                "stepfather",
                "grandparent"
            ])

            relationship_data = {
                "school_id": school_id,
                "parent_id": parent["id"],
                "student_id": student["id"],
                "relationship_type": relationship_type,
                "is_primary_contact": True,  # Since each student has only 1 parent
                "has_pickup_permission": self.faker.boolean(chance_of_getting_true=95),
                "can_approve_forms": self.faker.boolean(chance_of_getting_true=90),
                "receives_updates": True,
            }

            relationship = self.client.create_parent_student_relationship(relationship_data)

            # Track in cache
            self.cache.add_parent_student_relationship(
                parent["id"],
                student["id"],
                relationship_type
            )

            relationships.append(relationship)

        self._log_progress(f"✓ Created {len(relationships)} parent-student relationships")

        return relationships
