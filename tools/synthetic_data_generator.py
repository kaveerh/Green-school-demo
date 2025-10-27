#!/usr/bin/env python3
"""
Synthetic Test Data Generator for Green School Management System
Generates test data for implemented features: Users and Schools
Supports CSV and SQL export formats
"""

import csv
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse


class SyntheticDataGenerator:
    def __init__(self):
        self.schools_data = []
        self.users_data = []
        
        # Sample data pools
        self.school_names = [
            "Green Valley Primary", "Sunshine Elementary", "Oak Tree School",
            "Riverside Academy", "Mountain View Primary", "Cedar Grove School",
            "Maple Leaf Elementary", "Pine Hill Academy", "Willow Creek School",
            "Birch Wood Primary"
        ]
        
        self.first_names = [
            "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
            "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
            "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
            "Emily", "Daniel", "Elizabeth", "Matthew", "Sofia", "Jackson", "Avery"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ]
        
        self.domains = ["gmail.com", "yahoo.com", "outlook.com", "school.edu"]
        self.personas = ["Administrator", "Teacher", "Student", "Parent", "Vendor"]
        self.statuses = ["Active", "Inactive", "Suspended"]

    def generate_schools(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate synthetic school data"""
        schools = []
        used_names = set()
        
        for i in range(count):
            # Ensure unique school names
            name = random.choice(self.school_names)
            while name in used_names:
                name = random.choice(self.school_names)
            used_names.add(name)
            
            school_id = str(uuid.uuid4())
            created_at = datetime.now() - timedelta(days=random.randint(30, 365))
            
            school = {
                "id": school_id,
                "name": name,
                "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm'])} Street",
                "city": random.choice(["Springfield", "Riverside", "Greenville", "Franklin", "Georgetown"]),
                "state": random.choice(["CA", "NY", "TX", "FL", "IL"]),
                "postal_code": f"{random.randint(10000, 99999)}",
                "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "email": f"admin@{name.lower().replace(' ', '')}.edu",
                "website": f"https://www.{name.lower().replace(' ', '')}.edu",
                "principal_name": f"{random.choice(self.first_names)} {random.choice(self.last_names)}",
                "established_year": random.randint(1950, 2020),
                "student_capacity": random.randint(200, 1000),
                "grade_levels": "1,2,3,4,5,6,7",  # Grades 1-7 as per business rules
                "status": random.choice(["Active", "Inactive"]),
                "created_at": created_at.isoformat(),
                "updated_at": (created_at + timedelta(days=random.randint(0, 30))).isoformat(),
                "created_by": "system",
                "updated_by": "system",
                "deleted_at": None,
                "deleted_by": None
            }
            schools.append(school)
        
        self.schools_data = schools
        return schools

    def generate_users(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate synthetic user data"""
        if not self.schools_data:
            self.generate_schools()
        
        users = []
        
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            school = random.choice(self.schools_data)
            persona = random.choice(self.personas)
            
            user_id = str(uuid.uuid4())
            created_at = datetime.now() - timedelta(days=random.randint(1, 180))
            
            user = {
                "id": user_id,
                "school_id": school["id"],
                "keycloak_id": str(uuid.uuid4()),
                "email": f"{first_name.lower()}.{last_name.lower()}@{random.choice(self.domains)}",
                "first_name": first_name,
                "last_name": last_name,
                "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                "persona": persona,
                "status": random.choice(self.statuses),
                "last_login": (created_at + timedelta(days=random.randint(0, 30))).isoformat() if random.choice([True, False]) else None,
                "email_verified": random.choice([True, False]),
                "profile_picture_url": None,
                "preferences": json.dumps({
                    "theme": random.choice(["light", "dark"]),
                    "language": "en",
                    "notifications": random.choice([True, False])
                }),
                "created_at": created_at.isoformat(),
                "updated_at": (created_at + timedelta(days=random.randint(0, 30))).isoformat(),
                "created_by": "system",
                "updated_by": "system",
                "deleted_at": None,
                "deleted_by": None
            }
            users.append(user)
        
        self.users_data = users
        return users

    def export_csv(self, output_dir: str = "./"):
        """Export data to CSV files"""
        # Export schools
        if self.schools_data:
            with open(f"{output_dir}/schools.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.schools_data[0].keys())
                writer.writeheader()
                writer.writerows(self.schools_data)
            print(f"✅ Schools CSV exported: {output_dir}/schools.csv")
        
        # Export users
        if self.users_data:
            with open(f"{output_dir}/users.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.users_data[0].keys())
                writer.writeheader()
                writer.writerows(self.users_data)
            print(f"✅ Users CSV exported: {output_dir}/users.csv")

    def export_sql(self, output_dir: str = "./"):
        """Export data to SQL files"""
        # Export schools SQL
        if self.schools_data:
            with open(f"{output_dir}/schools.sql", 'w', encoding='utf-8') as f:
                f.write("-- Schools test data\n")
                f.write("-- Generated by Synthetic Data Generator\n\n")
                
                for school in self.schools_data:
                    values = []
                    for key, value in school.items():
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, str):
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        else:
                            values.append(str(value))
                    
                    columns = ", ".join(school.keys())
                    values_str = ", ".join(values)
                    f.write(f"INSERT INTO schools ({columns}) VALUES ({values_str});\n")
            print(f"✅ Schools SQL exported: {output_dir}/schools.sql")
        
        # Export users SQL
        if self.users_data:
            with open(f"{output_dir}/users.sql", 'w', encoding='utf-8') as f:
                f.write("-- Users test data\n")
                f.write("-- Generated by Synthetic Data Generator\n\n")
                
                for user in self.users_data:
                    values = []
                    for key, value in user.items():
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, str):
                            escaped_value = value.replace("'", "''")
                            values.append(f"'{escaped_value}'")
                        elif isinstance(value, bool):
                            values.append("TRUE" if value else "FALSE")
                        else:
                            values.append(str(value))
                    
                    columns = ", ".join(user.keys())
                    values_str = ", ".join(values)
                    f.write(f"INSERT INTO users ({columns}) VALUES ({values_str});\n")
            print(f"✅ Users SQL exported: {output_dir}/users.sql")

    def generate_summary(self):
        """Print generation summary"""
        print("\n📊 Data Generation Summary:")
        print(f"   Schools: {len(self.schools_data)}")
        print(f"   Users: {len(self.users_data)}")
        
        if self.users_data:
            persona_counts = {}
            status_counts = {}
            for user in self.users_data:
                persona_counts[user['persona']] = persona_counts.get(user['persona'], 0) + 1
                status_counts[user['status']] = status_counts.get(user['status'], 0) + 1
            
            print(f"\n   User Personas:")
            for persona, count in persona_counts.items():
                print(f"     {persona}: {count}")
            
            print(f"\n   User Statuses:")
            for status, count in status_counts.items():
                print(f"     {status}: {count}")


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic test data for Green School Management System')
    parser.add_argument('--schools', type=int, default=5, help='Number of schools to generate (default: 5)')
    parser.add_argument('--users', type=int, default=50, help='Number of users to generate (default: 50)')
    parser.add_argument('--format', choices=['csv', 'sql', 'both'], default='both', help='Export format (default: both)')
    parser.add_argument('--output', default='./', help='Output directory (default: current directory)')
    
    args = parser.parse_args()
    
    print("🏫 Green School Management System - Synthetic Data Generator")
    print("=" * 60)
    
    generator = SyntheticDataGenerator()
    
    # Generate data
    print(f"📝 Generating {args.schools} schools...")
    generator.generate_schools(args.schools)
    
    print(f"👥 Generating {args.users} users...")
    generator.generate_users(args.users)
    
    # Export data
    print(f"\n💾 Exporting data to {args.output}")
    if args.format in ['csv', 'both']:
        generator.export_csv(args.output)
    
    if args.format in ['sql', 'both']:
        generator.export_sql(args.output)
    
    # Show summary
    generator.generate_summary()
    
    print(f"\n✨ Data generation complete!")


if __name__ == "__main__":
    main()
