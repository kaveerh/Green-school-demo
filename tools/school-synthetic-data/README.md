# School Synthetic Data Generator

Generate realistic synthetic data for the Green School Management System. Perfect for testing, demos, and development.

## Features

- ✨ Generates data for all 15 system features
- 🔗 Properly links entities using UUIDs
- 🔍 Supports name-based and ID-based lookups
- ⚙️ Fully configurable via YAML
- 📊 Beautiful progress reporting
- 💾 Cache system for incremental generation
- 🎯 Realistic data using Faker library
- 🚀 Fast and reliable with retry logic

## Quick Start

### Installation

```bash
cd tools/school-synthetic-data
pip install -r requirements.txt
```

### Basic Usage

```bash
# Generate all data with default configuration
python -m src.main generate

# Generate small dataset (quick testing)
python -m src.main generate --config config/small.yaml

# Generate specific features only
python -m src.main generate --features students,classes,lessons
```

## What Gets Generated

| Feature | Description | Example Count |
|---------|-------------|---------------|
| **Schools** | School institution | 1 |
| **Users** | All user accounts | 112 |
| **Teachers** | Teacher profiles | 10 |
| **Parents** | Parent/guardian profiles | 50 |
| **Students** | Student profiles (Grades 1-7) | 50 |
| **Subjects** | Core & elective subjects | 6 |
| **Rooms** | Classrooms, labs, facilities | 15 |
| **Classes** | Subject-teacher-grade assignments | 42 |
| **Lessons** | Lesson plans | 1,260 |
| **Assessments** | Tests, quizzes, projects | 1,000 |
| **Attendance** | Daily attendance records | 4,500 |
| **Events** | School calendar events | 15 |
| **Activities** | Extracurricular activities | 5 |
| **Vendors** | School vendors/suppliers | 10 |
| **Merits** | Student awards/recognition | 250 |

**Total:** ~7,000+ records with proper relationships

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30

# Data Generation
SCHOOL_NAME="Green Valley Elementary School"
SCHOOL_CITY="Springfield"
SCHOOL_STATE="California"

# Output
LOG_LEVEL=INFO
EXPORT_CACHE=true
```

### YAML Configuration

The tool uses YAML files for detailed configuration. See `config/default.yaml` for all options.

#### Preset Configurations

**Small** (`config/small.yaml`) - Quick testing
- 3 teachers, 10 students
- Generates in ~1 minute

**Medium** (`config/medium.yaml`) - Demo/staging
- 10 teachers, 50 students
- Generates in ~5 minutes

**Large** (`config/large.yaml`) - Production-like
- 30 teachers, 200 students
- Generates in ~15 minutes

### Custom Configuration

Create your own config file:

```yaml
# custom_config.yaml
version: "1.0"

data_volumes:
  administrators: 2
  teachers: 15
  students: 75
  parents: 75
  subjects: 8
  rooms: 20
  classes: 30
  lessons_per_class: 40
  assessments_per_student: 25
  attendance_days: 120
  events: 20
  activities: 8
  vendors: 15
  merits_per_student: 8

generation_rules:
  grade_distribution:
    1: 10
    2: 11
    3: 11
    4: 11
    5: 11
    6: 11
    7: 10

  dates:
    academic_year_start: "2024-09-01"
    academic_year_end: "2025-06-30"
    current_quarter: "Q2"
```

Then use it:
```bash
python -m src.main generate --config custom_config.yaml
```

## CLI Commands

### Generate Data

```bash
# Generate all features
python -m src.main generate

# Generate with custom config
python -m src.main generate --config my_config.yaml

# Generate specific features only
python -m src.main generate --features students,classes,lessons

# Use existing cache (incremental)
python -m src.main generate --cache my_cache.json --features assessments
```

### Find Entities

```bash
# Find student by name
python -m src.main find --type student --name "John Doe"

# Find student by ID
python -m src.main find --type student --student-id "STU01001"

# Find teacher by name
python -m src.main find --type teacher --name "Jane Smith"

# Find parent by name
python -m src.main find --type parent --name "Robert Johnson"
```

### List Entities

```bash
# List all students
python -m src.main list --type students

# List all teachers
python -m src.main list --type teachers

# List all classes
python -m src.main list --type classes
```

### Cache Management

```bash
# Export cache
python -m src.main export-cache --output my_cache.json

# Import cache
python -m src.main import-cache --input my_cache.json

# View cache statistics
python -m src.main cache-stats
```

### Utilities

```bash
# Validate configuration file
python -m src.main validate-config --config my_config.yaml

# Clean up all generated data (CAREFUL!)
python -m src.main cleanup --confirm

# Show help
python -m src.main --help
```

## How It Works

### Generation Order

The tool generates data in a specific order to respect dependencies:

1. **School** - Foundation for all data
2. **Users** - Base accounts (administrators, teachers, parents, students)
3. **Teachers** - Teacher profiles linked to users
4. **Parents** - Parent profiles linked to users
5. **Students** - Student profiles linked to users
6. **Parent-Student Links** - Each student gets 1 parent
7. **Subjects** - Academic subjects (MATH, ELA, etc.)
8. **Rooms** - Classrooms, labs, gym, etc.
9. **Classes** - Subject + Teacher + Grade + Room
10. **Student-Class Enrollments** - Enroll students in classes
11. **Lessons** - Lesson plans for each class
12. **Assessments** - Tests, quizzes, projects per student
13. **Attendance** - Daily attendance records
14. **Events** - School calendar events
15. **Activities** - Extracurricular activities
16. **Vendors** - School vendors/suppliers
17. **Merits** - Student awards and recognition

### UUID Management

The tool tracks all generated UUIDs in a cache and supports human-friendly lookups:

- **Find by name**: "John Doe" → UUID
- **Find by email**: "john.doe@school.edu" → UUID
- **Find by Student ID**: "STU01001" → UUID
- **Random selection**: Get random entities for linking

### Realistic Data

Uses [Faker](https://faker.readthedocs.io/) to generate:
- Real-looking names
- Valid email addresses
- Realistic addresses and phone numbers
- Proper date ranges
- Varied distributions (90% present, 5% absent, etc.)

## Examples

### Generate Small Dataset for Quick Testing

```bash
python -m src.main generate --config config/small.yaml
```

Output:
```
🚀 Starting Green School Data Generator

[1/17] Generating school...
   ✓ Created school: Green Valley Elementary School

[2/17] Generating users...
   ✓ Created 2 administrators
   ✓ Created 3 teachers
   ✓ Created 10 students
   ✓ Created 10 parents

... (continues for all 17 steps)

✅ Data generation complete!

Summary:
  Schools: 1
  Users: 25
  Students: 10
  Classes: 6
  Lessons: 60
  Total records: ~500

Cache exported to: generated_data_cache.json
Time taken: 45 seconds
```

### Generate Specific Features Only

```bash
# Already have basic data, just need more assessments
python -m src.main generate \
  --cache generated_data_cache.json \
  --features assessments,attendance
```

### Find a Student

```bash
python -m src.main find --type student --name "Emma Wilson"
```

Output:
```json
{
  "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "student_id": "STU01015",
  "user_id": "b2c3d4e5-6789-01bc-def0-234567890abc",
  "first_name": "Emma",
  "last_name": "Wilson",
  "grade_level": 3,
  "email": "emma.wilson@greenvalley.edu",
  "status": "enrolled"
}
```

### Generate Data for Specific Grade Levels Only

Create `grade_3_only.yaml`:
```yaml
data_volumes:
  teachers: 5
  students: 15

generation_rules:
  grade_distribution:
    3: 15  # Only grade 3 students
```

Run:
```bash
python -m src.main generate --config grade_3_only.yaml
```

## Troubleshooting

### "Connection refused" error

Make sure the API server is running:
```bash
cd backend
docker-compose up -d
```

### "Not enough parents for students" error

Increase parent count in config:
```yaml
data_volumes:
  parents: 50  # Must be >= students count
```

### Slow generation

Use smaller dataset for testing:
```bash
python -m src.main generate --config config/small.yaml
```

### API validation errors

Check the generated data in logs:
```bash
python -m src.main generate --log-level DEBUG
```

### Cache out of sync

Delete cache and regenerate:
```bash
rm generated_data_cache.json
python -m src.main generate
```

## Best Practices

1. **Start Small**: Use `small.yaml` for initial testing
2. **Use Cache**: Save cache file for incremental generation
3. **Validate First**: Run `validate-config` before long generations
4. **Check Logs**: Use `--log-level DEBUG` to troubleshoot
5. **Version Control**: Don't commit cache files (add to `.gitignore`)
6. **Clean Data**: Use `cleanup` command before regenerating

## Architecture

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md).

Key components:
- **Cache System**: Tracks all UUIDs and enables lookups
- **API Client**: Handles all HTTP requests with retry logic
- **Generators**: One per entity type (17 total)
- **Orchestrator**: Manages generation order and dependencies
- **Config Loader**: Parses and validates YAML configuration

## Requirements

- Python 3.9+
- Running instance of Green School Management System API
- Internet connection (for Faker data generation)

## Dependencies

See `requirements.txt`:
- `faker` - Generate realistic fake data
- `requests` - HTTP client
- `pyyaml` - Configuration management
- `python-dotenv` - Environment variables
- `click` - CLI framework
- `rich` - Beautiful terminal output
- `pydantic` - Data validation

## Development

### Running Tests

```bash
pytest tests/
```

### Adding Custom Generator

1. Create new generator in `src/generators/my_feature.py`
2. Inherit from `BaseGenerator`
3. Implement `generate()` method
4. Register in `DataGenerator.__init__()`
5. Add to generation order in `generate_all()`

Example:
```python
class MyFeatureGenerator(BaseGenerator):
    def generate(self, count: int, **kwargs) -> List[dict]:
        entities = []
        # Your generation logic here
        return entities
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: [project-repo/issues]
- Documentation: See `ARCHITECTURE.md`
- API Docs: http://localhost:8000/docs

## License

[To be determined - should match main project]

## Changelog

### Version 1.0.0 (Planned)
- Initial release
- Support for all 15 features
- CLI interface
- YAML configuration
- Cache system with lookups
- Progress reporting
- Error handling and retry logic
