# Tools Directory

This directory contains utility tools for the Green School Management System project.

## Synthetic Data Generator

`synthetic_data_generator.py` - Generates realistic test data for implemented features.

### Features
- Generates data for Users and Schools (implemented features)
- Exports to CSV and SQL formats
- Configurable data volumes
- Realistic sample data with proper relationships

### Usage

```bash
# Basic usage (generates 5 schools, 50 users, both CSV and SQL)
python tools/synthetic_data_generator.py

# Custom parameters
python tools/synthetic_data_generator.py --schools 10 --users 100 --format csv --output ./test-data/

# Help
python tools/synthetic_data_generator.py --help
```

### Parameters
- `--schools`: Number of schools to generate (default: 5)
- `--users`: Number of users to generate (default: 50)
- `--format`: Export format - csv, sql, or both (default: both)
- `--output`: Output directory (default: current directory)

### Generated Data

#### Schools
- Unique school names and details
- Realistic addresses and contact information
- Grades 1-7 support (per business rules)
- Principal names and establishment years
- Active/Inactive status

#### Users
- Distributed across generated schools
- All 5 personas: Administrator, Teacher, Student, Parent, Vendor
- Realistic names and email addresses
- Various statuses: Active, Inactive, Suspended
- Proper UUID relationships

### Output Files
- `schools.csv` / `schools.sql` - School data
- `users.csv` / `users.sql` - User data

### Example Output
```
🏫 Green School Management System - Synthetic Data Generator
============================================================
📝 Generating 5 schools...
👥 Generating 50 users...

💾 Exporting data to ./
✅ Schools CSV exported: ./schools.csv
✅ Users CSV exported: ./users.csv
✅ Schools SQL exported: ./schools.sql
✅ Users SQL exported: ./users.sql

📊 Data Generation Summary:
   Schools: 5
   Users: 50

   User Personas:
     Administrator: 8
     Teacher: 12
     Student: 15
     Parent: 10
     Vendor: 5

   User Statuses:
     Active: 35
     Inactive: 10
     Suspended: 5

✨ Data generation complete!
```
