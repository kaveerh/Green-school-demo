"""
User Generator

Generate user accounts for all personas (administrator, teacher, student, parent, vendor).
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class UserGenerator(BaseGenerator):
    """
    Generate user accounts

    Responsibilities:
    - Create users for all personas
    - Generate realistic names and emails
    - Set appropriate status
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate user accounts

        Args:
            count: Not used (counts from config)
            **kwargs: persona (required) - 'administrator', 'teacher', 'student', 'parent', 'vendor'

        Returns:
            List of generated user dictionaries
        """
        persona = kwargs.get("persona")
        if not persona:
            raise ValueError("persona parameter is required")

        # Get count from config
        data_volumes = self.config.get("data_volumes", {})

        if persona == "administrator":
            count = data_volumes.get("administrators", 2)
        elif persona == "teacher":
            count = data_volumes.get("teachers", 10)
        elif persona == "student":
            count = data_volumes.get("students", 50)
        elif persona == "parent":
            count = data_volumes.get("parents", 50)
        elif persona == "vendor":
            count = data_volumes.get("vendors", 10)
        else:
            raise ValueError(f"Unknown persona: {persona}")

        users = []
        school_id = self._get_school_id()
        domain = self._get_school_domain()

        self._log_progress(f"Creating {count} {persona} users")

        for i in range(count):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = self._generate_email(first_name, last_name, domain)

            # Ensure unique email
            attempt = 1
            while self.cache.find_user_by_email(email):
                email = self._generate_email(f"{first_name}{attempt}", last_name, domain)
                attempt += 1

            user_data = {
                "school_id": school_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "persona": persona,
                "status": "active",
                "phone": self._generate_phone(),
                "password": self._generate_password(),
            }

            user = self.client.create_user(user_data)
            self.cache.add_entity("user", user["id"], user)
            users.append(user)

        self._log_progress(f"✓ Created {len(users)} {persona} users")

        return users
