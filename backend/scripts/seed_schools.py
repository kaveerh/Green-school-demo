"""
Seed script for schools table
Creates 5 sample schools for testing
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from config.database import async_session
from models.school import School
from models.user import User


async def seed_schools():
    """Seed schools table with sample data"""
    async with async_session() as session:
        # Check if schools already exist
        result = await session.execute(select(School).limit(1))
        existing = result.scalar_one_or_none()

        if existing and existing.name != "Green Valley Elementary":
            print("Schools already seeded. Skipping...")
            return

        # Get the first admin user for created_by
        result = await session.execute(
            select(User)
            .where(User.persona == "administrator")
            .limit(1)
        )
        admin_user = result.scalar_one_or_none()
        admin_id = admin_user.id if admin_user else None

        schools_data = [
            {
                "name": "Green Valley Elementary",
                "slug": "green-valley",
                "address_line1": "123 Main Street",
                "city": "Springfield",
                "state": "IL",
                "postal_code": "62701",
                "country": "USA",
                "phone": "+1-217-555-0100",
                "email": "info@greenvalley.edu",
                "website_url": "https://greenvalley.edu",
                "facebook_url": "https://facebook.com/greenvalleyelementary",
                "twitter_url": "https://twitter.com/greenvalley_edu",
                "timezone": "America/Chicago",
                "status": "active",
                "settings": {
                    "school_year_start": "08-15",
                    "school_year_end": "06-15",
                    "grading_scale": "letter",
                    "attendance_tracking": "enabled"
                },
                "created_by": admin_id,
                "updated_by": admin_id
            },
            {
                "name": "Riverside Primary School",
                "slug": "riverside-primary",
                "address_line1": "456 River Road",
                "city": "Portland",
                "state": "OR",
                "postal_code": "97201",
                "country": "USA",
                "phone": "+1-503-555-0200",
                "email": "hello@riverside.edu",
                "website_url": "https://riverside.edu",
                "instagram_url": "https://instagram.com/riversideprimary",
                "timezone": "America/Los_Angeles",
                "status": "active",
                "settings": {
                    "school_year_start": "09-01",
                    "school_year_end": "06-30",
                    "grading_scale": "percentage"
                },
                "created_by": admin_id,
                "updated_by": admin_id
            },
            {
                "name": "Oakwood Academy",
                "slug": "oakwood-academy",
                "address_line1": "789 Oak Avenue",
                "address_line2": "Suite 100",
                "city": "Boston",
                "state": "MA",
                "postal_code": "02101",
                "country": "USA",
                "phone": "+1-617-555-0300",
                "email": "admin@oakwood.edu",
                "website_url": "https://oakwood.academy",
                "facebook_url": "https://facebook.com/oakwoodacademy",
                "twitter_url": "https://twitter.com/oakwood_academy",
                "timezone": "America/New_York",
                "status": "active",
                "settings": {
                    "school_year_start": "08-20",
                    "school_year_end": "06-10"
                },
                "created_by": admin_id,
                "updated_by": admin_id
            },
            {
                "name": "Sunshine Elementary",
                "slug": "sunshine-elementary",
                "address_line1": "321 Sunshine Boulevard",
                "city": "Miami",
                "state": "FL",
                "postal_code": "33101",
                "country": "USA",
                "phone": "+1-305-555-0400",
                "email": "contact@sunshine.edu",
                "website_url": "https://sunshine.edu",
                "instagram_url": "https://instagram.com/sunshineschool",
                "timezone": "America/New_York",
                "status": "active",
                "settings": {
                    "school_year_start": "08-10",
                    "school_year_end": "05-31",
                    "bilingual": True
                },
                "created_by": admin_id,
                "updated_by": admin_id
            },
            {
                "name": "Meadowbrook School",
                "slug": "meadowbrook",
                "address_line1": "987 Meadow Lane",
                "city": "Austin",
                "state": "TX",
                "postal_code": "73301",
                "country": "USA",
                "phone": "+1-512-555-0500",
                "email": "info@meadowbrook.edu",
                "website_url": "https://meadowbrook.edu",
                "facebook_url": "https://facebook.com/meadowbrookschool",
                "timezone": "America/Chicago",
                "status": "inactive",
                "settings": {
                    "school_year_start": "08-25",
                    "school_year_end": "06-05"
                },
                "created_by": admin_id,
                "updated_by": admin_id
            }
        ]

        # Check if we need to update Green Valley or insert all
        result = await session.execute(
            select(School).where(School.name == "Green Valley Elementary")
        )
        green_valley = result.scalar_one_or_none()

        if green_valley:
            print("Updating existing Green Valley Elementary school...")
            for key, value in schools_data[0].items():
                if hasattr(green_valley, key):
                    setattr(green_valley, key, value)

            # Add the rest
            for school_data in schools_data[1:]:
                school = School(**school_data)
                session.add(school)
                print(f"Adding school: {school_data['name']}")
        else:
            # Add all schools
            for school_data in schools_data:
                school = School(**school_data)
                session.add(school)
                print(f"Adding school: {school_data['name']}")

        await session.commit()
        print(f"\n✅ Successfully seeded {len(schools_data)} schools")


if __name__ == "__main__":
    asyncio.run(seed_schools())
