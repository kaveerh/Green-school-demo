"""
Parent Generator

Generate parent profiles linked to user accounts.
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class ParentGenerator(BaseGenerator):
    """
    Generate parent profiles

    Responsibilities:
    - Link parent profiles to users with 'parent' persona
    - Set contact preferences
    - Configure permissions
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate parent profiles

        Args:
            count: Number of parents (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated parent dictionaries
        """
        parents = []
        school_id = self._get_school_id()

        # Get all parent users
        parent_users = [u for u in self.cache.users.values() if u.get("persona") == "parent"]

        if not parent_users:
            raise ValueError("No parent users found in cache. Generate parent users first.")

        self._log_progress(f"Creating {len(parent_users)} parent profiles")

        for user in parent_users:
            parent_data = {
                "school_id": school_id,
                "user_id": user["id"],
                "occupation": self.faker.job(),
                "workplace": self.faker.company(),
                "phone_mobile": self.faker.phone_number(),
                "phone_work": self.faker.phone_number() if self.faker.boolean(chance_of_getting_true=60) else None,
                "preferred_contact_method": self.faker.random_element([
                    "email", "phone", "sms", "app_notification"
                ]),
                "emergency_contact": self.faker.boolean(chance_of_getting_true=80),
                "pickup_authorized": self.faker.boolean(chance_of_getting_true=90),
                "receives_newsletter": self.faker.boolean(chance_of_getting_true=85),
            }

            parent = self.client.create_parent(parent_data)

            # Store with user info for easier lookup
            parent_with_user = {
                **parent,
                "user": user,
            }

            self.cache.add_entity("parent", parent["id"], parent_with_user)
            parents.append(parent)

        self._log_progress(f"✓ Created {len(parents)} parent profiles")

        return parents
