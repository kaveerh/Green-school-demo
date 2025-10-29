"""
School Generator

Generate school records.
"""
from typing import List, Dict, Any
from .base import BaseGenerator


class SchoolGenerator(BaseGenerator):
    """
    Generate school records

    Responsibilities:
    - Create school with complete address
    - Set timezone and locale
    - Generate contact information
    """

    def generate(self, count: int = 1, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate school records

        Args:
            count: Number of schools to generate (usually 1)
            **kwargs: Additional parameters

        Returns:
            List of generated school dictionaries
        """
        schools = []

        # Get school config
        school_config = self.config.get("school", {})

        # Only generate one school (multi-tenant by school_id)
        school_name = school_config.get("name", "Green Valley Elementary School")
        slug = school_config.get("slug", "green-valley-elementary")
        city = school_config.get("city", "Springfield")
        state = school_config.get("state", "California")
        country = school_config.get("country", "USA")
        postal_code = school_config.get("postal_code", "90210")
        timezone = school_config.get("timezone", "America/Los_Angeles")
        locale = school_config.get("locale", "en_US")
        domain = school_config.get("domain", "greenvalley.edu")

        # Check if school already exists
        try:
            response = self.client.get("/api/v1/schools")
            existing_schools = response.get("data", [])
            
            # Look for school with matching slug
            for existing_school in existing_schools:
                if existing_school.get("slug") == slug:
                    self._log_progress(f"Using existing school: {school_name} (ID: {existing_school['id']})")
                    self.cache.add_entity("school", existing_school["id"], existing_school)
                    schools.append(existing_school)
                    return schools
        except Exception as e:
            self._log_progress(f"Could not check for existing schools: {e}")

        school_data = {
            "name": school_name,
            "slug": slug,
            "address_line1": self.faker.street_address(),
            "address_line2": None,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "country": country,
            "phone": self.faker.phone_number(),
            "email": f"admin@{domain}",
            "website_url": f"https://www.{domain}",
            "timezone": timezone,
            "locale": locale,
            "status": "active",
        }

        self._log_progress(f"Creating school: {school_name}")

        school = self.client.create_school(school_data)
        self.cache.add_entity("school", school["id"], school)

        schools.append(school)

        self._log_progress(f"✓ Created school: {school_name} (ID: {school['id']})")

        return schools
