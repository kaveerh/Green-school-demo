"""
Subject Generator

Generate academic subjects based on configuration.
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class SubjectGenerator(BaseGenerator):
    """
    Generate subject records

    Responsibilities:
    - Create subjects from configuration
    - Set grade levels, colors, categories
    - Configure requirements
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate subject records from configuration

        Args:
            count: Not used (subjects from config)
            **kwargs: Additional parameters

        Returns:
            List of generated subject dictionaries
        """
        subjects = []
        school_id = self._get_school_id()

        # Get subjects from config
        subject_configs = self.config.get("generation_rules", {}).get("subjects", [])

        if not subject_configs:
            raise ValueError("No subjects configured in generation_rules.subjects")

        self._log_progress(f"Creating {len(subject_configs)} subjects")

        for i, subject_config in enumerate(subject_configs):
            subject_data = {
                "school_id": school_id,
                "code": subject_config["code"],
                "name": subject_config["name"],
                "description": f"Primary school {subject_config['name']} curriculum for grades {min(subject_config['grade_levels'])}-{max(subject_config['grade_levels'])}",
                "category": subject_config["category"],
                "subject_type": subject_config.get("subject_type", "academic"),
                "grade_levels": subject_config["grade_levels"],
                "color": subject_config.get("color", "#757575"),
                "icon": subject_config.get("icon"),
                "display_order": i,
                "is_required": subject_config.get("is_required", True),
                "is_active": True,
            }

            subject = self.client.create_subject(subject_data)
            self.cache.add_entity("subject", subject["id"], subject)
            subjects.append(subject)

        self._log_progress(f"✓ Created {len(subjects)} subjects")

        return subjects
