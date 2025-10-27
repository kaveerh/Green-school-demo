# Quick Start Guide

Get up and running with the School Synthetic Data Generator in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- Green School Management System API running at http://localhost:8000
- pip package manager

## Installation

```bash
# Navigate to the tool directory
cd tools/school-synthetic-data

# Install dependencies
pip install -r requirements.txt

# Create environment file (optional)
cp .env.example .env
```

## Generate Your First Dataset

### Option 1: Small Dataset (Quick Test - 1 minute)

Perfect for testing and development:

```bash
python -m src.main generate --config config/small.yaml
```

This generates:
- 1 school
- 10 students, 3 teachers, 10 parents
- 4 subjects, 8 rooms, 6 classes
- 60 lessons, 50 assessments
- 300 attendance records
- **Total: ~500 records in ~1 minute**

### Option 2: Medium Dataset (Demo - 5 minutes)

Good for demos and staging:

```bash
python -m src.main generate --config config/medium.yaml
# OR simply:
python -m src.main generate
```

This generates:
- 1 school
- 50 students, 10 teachers, 50 parents
- 6 subjects, 15 rooms, 42 classes
- 1,260 lessons, 1,000 assessments
- 4,500 attendance records
- **Total: ~7,500 records in ~5 minutes**

## What Happens During Generation

You'll see progress output like this:

```
🚀 Starting Green School Data Generator

Configuration: config/small.yaml
API URL: http://localhost:8000

[1/20] Generating School...
   ✓ Generated 1 School

[2/20] Generating Administrator Users...
   ✓ Generated 1 Administrator Users

[3/20] Generating Teacher Users...
   ✓ Generated 3 Teacher Users

... (continues for all 20 steps)

✅ Data generation complete!

╭─ Generation Statistics ─╮
│ Entity Type         Count│
├─────────────────────────┤
│ Schools                 1│
│ Users                  14│
│ Teachers                3│
│ Students               10│
│ ...                      │
╰─────────────────────────╯

Total Records: 512

✓ Exported cache to: generated_data_cache_small.json
```

## Verify the Data

### Check via API

```bash
# Get school info
curl http://localhost:8000/api/v1/schools | jq

# List users
curl http://localhost:8000/api/v1/users | jq

# List students
curl http://localhost:8000/api/v1/students | jq
```

### Search from Cache

```bash
# Find student by name
python -m src.main find --type student --name "Emma Wilson"

# Find student by ID
python -m src.main find --type student --student-id "STU01001"

# List all students
python -m src.main list --type students --limit 20

# Show cache statistics
python -m src.main cache-stats --cache generated_data_cache_small.json
```

## Common Use Cases

### Generate Only Specific Features

```bash
# Already have basic data, just need more assessments
python -m src.main generate \
  --cache generated_data_cache.json \
  --features assessments,attendance
```

### Use Custom Configuration

```bash
# Create your config
cp config/small.yaml my_config.yaml
# Edit my_config.yaml with your settings

# Generate with your config
python -m src.main generate --config my_config.yaml
```

### Export Data for Analysis

```bash
# Export cache to different file
python -m src.main export-cache \
  --cache generated_data_cache.json \
  --output my_export.json
```

## Troubleshooting

### "Connection refused"

**Problem**: Can't connect to API

**Solution**: Make sure the backend is running
```bash
cd backend
docker-compose up -d
# Check it's running
curl http://localhost:8000/docs
```

### "Configuration error"

**Problem**: Invalid config file

**Solution**: Validate your config
```bash
python -m src.main validate-config --config my_config.yaml
```

### Generation is slow

**Problem**: Taking too long

**Solution**: Use smaller dataset first
```bash
python -m src.main generate --config config/small.yaml
```

### Want to see more details

**Problem**: Need debug info

**Solution**: Enable debug logging
```bash
python -m src.main generate --log-level DEBUG
```

## Next Steps

- Read the full [README.md](./README.md) for all features
- Check [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- Browse [config/](./config/) for configuration examples
- Customize data volumes and generation rules

## Getting Help

If you encounter issues:
1. Check the API is running: http://localhost:8000/docs
2. Validate your config: `python -m src.main validate-config --config your_config.yaml`
3. Enable debug logging: `--log-level DEBUG`
4. Check generated cache file for what was created
5. Review error messages in console output

## Clean Up

To remove generated data:
```bash
# Delete cache file
rm generated_data_cache*.json

# Note: To delete from database, you'd need to use the API
# or connect directly to PostgreSQL
```

---

**Happy Data Generating! 🚀**
