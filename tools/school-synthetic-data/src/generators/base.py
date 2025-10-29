"""
Base Generator

Abstract base class for all entity generators.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from faker import Faker
import logging

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    Abstract base class for entity generators

    Handles:
    - Faker instance management
    - Cache access
    - API client access
    - Common generation patterns
    """

    def __init__(self, client, cache, faker: Faker, config: Dict[str, Any]):
        """
        Initialize generator

        Args:
            client: SchoolAPIClient instance
            cache: EntityCache instance
            faker: Faker instance
            config: Configuration dictionary
        """
        self.client = client
        self.cache = cache
        self.faker = faker
        self.config = config

    @abstractmethod
    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate entities

        Args:
            count: Number of entities to generate
            **kwargs: Additional generation parameters

        Returns:
            List of generated entity dictionaries
        """
        pass

    def _generate_address(self) -> Dict[str, str]:
        """Generate realistic address"""
        return {
            "address_line1": self.faker.street_address(),
            "address_line2": self.faker.secondary_address() if self.faker.boolean(chance_of_getting_true=20) else None,
            "city": self.faker.city(),
            "state": self.faker.state_abbr(),
            "postal_code": self.faker.postcode(),
            "country": "USA",
        }

    def _generate_phone(self) -> str:
        """Generate phone number (max 20 chars, valid format)"""
        # Generate simple US phone format: +1-XXX-XXX-XXXX
        area_code = self.faker.random_int(min=200, max=999)
        exchange = self.faker.random_int(min=200, max=999)
        number = self.faker.random_int(min=1000, max=9999)
        return f"+1-{area_code}-{exchange}-{number}"

    def _generate_email(self, first_name: str, last_name: str, domain: str) -> str:
        """
        Generate email address

        Args:
            first_name: First name
            last_name: Last name
            domain: Email domain (e.g., 'greenvalley.edu')

        Returns:
            Email address
        """
        # Clean names (remove special chars, lowercase)
        first = first_name.lower().replace(" ", "").replace("'", "")
        last = last_name.lower().replace(" ", "").replace("'", "")

        # Format: firstname.lastname@domain
        return f"{first}.{last}@{domain}"

    def _generate_password(self) -> str:
        """Generate default password"""
        # In production, this would be more secure
        # For testing, use simple default passwords
        return "Password123!"

    def _get_school_id(self) -> str:
        """Get the school ID from cache"""
        schools = list(self.cache.schools.values())
        if not schools:
            raise ValueError("No school found in cache. Generate school first.")
        return schools[0]["id"]

    def _get_school_domain(self) -> str:
        """Get the school email domain from cache"""
        schools = list(self.cache.schools.values())
        if not schools:
            raise ValueError("No school found in cache. Generate school first.")
        email = schools[0].get("email", "school@example.edu")
        return email.split("@")[1]

    def _log_progress(self, message: str) -> None:
        """Log progress message"""
        logger.info(message)
