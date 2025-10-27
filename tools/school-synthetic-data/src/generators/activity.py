"""
Activity Generator

Generate extracurricular activity records.
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class ActivityGenerator(BaseGenerator):
    """
    Generate activity records

    Responsibilities:
    - Create extracurricular activities
    - Set schedules and capacity
    - Assign coordinators
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate activity records

        Args:
            count: Number of activities (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated activity dictionaries
        """
        activities = []
        school_id = self._get_school_id()

        # Get activity types from config
        activity_types_config = self.config.get("generation_rules", {}).get("activity_types", {})

        if not activity_types_config:
            raise ValueError("No activity types configured")

        total_activities = sum(activity_types_config.values())

        # Get teachers for coordinators
        teachers = list(self.cache.teachers.values())

        if not teachers:
            raise ValueError("No teachers found. Generate teachers first.")

        self._log_progress(f"Creating {total_activities} activities")

        for activity_type, count in activity_types_config.items():
            for i in range(count):
                # Activity names by type
                if activity_type == "sports":
                    name = self.faker.random_element([
                        "Basketball Team",
                        "Soccer Club",
                        "Track and Field",
                        "Swimming Team",
                        "Volleyball Club"
                    ])
                elif activity_type == "arts":
                    name = self.faker.random_element([
                        "Drama Club",
                        "Art Club",
                        "Music Ensemble",
                        "Dance Team",
                        "Choir"
                    ])
                elif activity_type == "academic":
                    name = self.faker.random_element([
                        "Science Club",
                        "Math Team",
                        "Debate Club",
                        "Chess Club",
                        "Robotics Team"
                    ])
                elif activity_type == "community":
                    name = self.faker.random_element([
                        "Student Council",
                        "Community Service Club",
                        "Environmental Club",
                        "Peer Tutoring",
                        "School Newspaper"
                    ])
                else:
                    name = f"{activity_type.title()} Activity {i + 1}"

                # Pick a coordinator (teacher)
                coordinator = self.faker.random_element(teachers)

                # Schedule
                days_of_week = self.faker.random_elements(
                    elements=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    length=self.faker.random_int(min=1, max=3),
                    unique=True
                )

                activity_data = {
                    "school_id": school_id,
                    "name": name,
                    "description": f"{name} for students interested in {activity_type}",
                    "activity_type": activity_type,
                    "coordinator_id": coordinator["user"]["id"],
                    "meeting_schedule": {
                        "days": days_of_week,
                        "time": self.faker.random_element([
                            "15:00", "15:30", "16:00", "07:30"  # After school or before school
                        ]),
                        "duration_minutes": self.faker.random_element([45, 60, 90])
                    },
                    "max_participants": self.faker.random_int(min=10, max=30),
                    "current_participants": 0,
                    "grade_levels": self.faker.random_elements(
                        elements=[1, 2, 3, 4, 5, 6, 7],
                        length=self.faker.random_int(min=3, max=7),
                        unique=True
                    ),
                    "is_active": True,
                    "requires_tryout": activity_type == "sports" and self.faker.boolean(chance_of_getting_true=50),
                    "has_fee": self.faker.boolean(chance_of_getting_true=20),
                }

                activity = self.client.create_activity(activity_data)
                self.cache.add_entity("activity", activity["id"], activity)
                activities.append(activity)

        self._log_progress(f"✓ Created {len(activities)} activities")

        return activities
