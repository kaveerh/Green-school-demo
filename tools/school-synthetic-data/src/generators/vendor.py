"""
Vendor Generator

Generate vendor/supplier records.
"""
from typing import List, Dict, Any
from datetime import date, timedelta
from .base import BaseGenerator


class VendorGenerator(BaseGenerator):
    """
    Generate vendor records

    Responsibilities:
    - Create vendor profiles for school suppliers
    - Set contract details
    - Assign vendor types and statuses
    """

    def generate(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate vendor records

        Args:
            count: Number of vendors (from config)
            **kwargs: Additional parameters

        Returns:
            List of generated vendor dictionaries
        """
        vendors = []
        school_id = self._get_school_id()

        # Get vendor types from config
        vendor_types_config = self.config.get("generation_rules", {}).get("vendor_types", {})

        if not vendor_types_config:
            raise ValueError("No vendor types configured")

        total_vendors = sum(vendor_types_config.values())

        self._log_progress(f"Creating {total_vendors} vendors")

        for vendor_type, count in vendor_types_config.items():
            for i in range(count):
                # Company names by type
                if vendor_type == "food_service":
                    company_name = self.faker.random_element([
                        "Healthy Meals Inc",
                        "Fresh Food Services",
                        "School Lunch Co",
                        "Nutrition Plus",
                        "Cafeteria Partners"
                    ])
                elif vendor_type == "supplies":
                    company_name = self.faker.random_element([
                        "Office Supply Depot",
                        "School Supplies Plus",
                        "Educational Materials Co",
                        "Classroom Essentials",
                        "Teachers' Choice Supply"
                    ])
                elif vendor_type == "maintenance":
                    company_name = self.faker.random_element([
                        "Facilities Maintenance Group",
                        "Clean & Safe Services",
                        "BuildingCare Pro",
                        "Maintenance Masters",
                        "Facility Solutions Inc"
                    ])
                elif vendor_type == "it_services":
                    company_name = self.faker.random_element([
                        "Tech Support Pro",
                        "IT Solutions Group",
                        "Computer Services Inc",
                        "Network Experts",
                        "Digital Learning Tech"
                    ])
                elif vendor_type == "transportation":
                    company_name = self.faker.random_element([
                        "Safe Routes Transportation",
                        "School Bus Services",
                        "Student Transit Co",
                        "Yellow Bus Company",
                        "Educational Transport Inc"
                    ])
                elif vendor_type == "events":
                    company_name = self.faker.random_element([
                        "Event Planning Pro",
                        "School Events Inc",
                        "Celebration Services",
                        "Party Planners Plus",
                        "Special Occasions Co"
                    ])
                else:
                    company_name = f"{self.faker.company()} {vendor_type.replace('_', ' ').title()}"

                # Contract dates
                contract_start = date.today() - timedelta(days=self.faker.random_int(min=30, max=730))
                contract_end = contract_start + timedelta(days=self.faker.random_int(min=365, max=1095))

                # Contract value
                if vendor_type == "food_service":
                    contract_value = self.faker.random_int(min=50000, max=200000)
                elif vendor_type == "transportation":
                    contract_value = self.faker.random_int(min=80000, max=300000)
                else:
                    contract_value = self.faker.random_int(min=10000, max=100000)

                # Status
                status = self.faker.random_element([
                    "active", "active", "active",  # Most should be active
                    "pending", "inactive"
                ])

                vendor_data = {
                    "school_id": school_id,
                    "company_name": company_name,
                    "vendor_type": vendor_type,
                    "status": status,
                    "contact_person": self.faker.name(),
                    "contact_email": self.faker.company_email(),
                    "contact_phone": self.faker.phone_number(),
                    "address_line1": self.faker.street_address(),
                    "city": self.faker.city(),
                    "state": self.faker.state_abbr(),
                    "postal_code": self.faker.postcode(),
                    "country": "USA",
                    "website_url": f"https://www.{company_name.lower().replace(' ', '')}.com",
                    "tax_id": self.faker.random_number(digits=9, fix_len=True),
                    "contract_start_date": contract_start.isoformat(),
                    "contract_end_date": contract_end.isoformat(),
                    "contract_value": float(contract_value),
                    "payment_terms": self.faker.random_element([
                        "Net 30", "Net 60", "Due on Receipt", "Monthly", "Quarterly"
                    ]),
                    "services_provided": [
                        f"{vendor_type.replace('_', ' ').title()} service {j + 1}"
                        for j in range(self.faker.random_int(min=1, max=3))
                    ],
                    "performance_rating": round(self.faker.random.uniform(3.5, 5.0), 2),
                    "preferred": self.faker.boolean(chance_of_getting_true=30),
                    "insurance_expiry": (date.today() + timedelta(days=365)).isoformat(),
                }

                vendor = self.client.create_vendor(vendor_data)
                self.cache.add_entity("vendor", vendor["id"], vendor)
                vendors.append(vendor)

        self._log_progress(f"✓ Created {len(vendors)} vendors")

        return vendors
