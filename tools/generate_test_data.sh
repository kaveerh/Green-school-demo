#!/bin/bash

# Generate Test Data for Green School Management System
# Quick script to generate different data sets

echo "🏫 Green School Management System - Test Data Generation"
echo "========================================================"

# Create output directory
mkdir -p test-data

echo "📝 Generating small dataset (3 schools, 20 users)..."
python3 tools/synthetic_data_generator.py --schools 3 --users 20 --output test-data/small/
mkdir -p test-data/small

echo "📝 Generating medium dataset (5 schools, 50 users)..."
python3 tools/synthetic_data_generator.py --schools 5 --users 50 --output test-data/medium/
mkdir -p test-data/medium

echo "📝 Generating large dataset (10 schools, 100 users)..."
python3 tools/synthetic_data_generator.py --schools 10 --users 100 --output test-data/large/
mkdir -p test-data/large

echo "📝 Generating CSV-only dataset (5 schools, 30 users)..."
python3 tools/synthetic_data_generator.py --schools 5 --users 30 --format csv --output test-data/csv-only/
mkdir -p test-data/csv-only

echo "📝 Generating SQL-only dataset (5 schools, 30 users)..."
python3 tools/synthetic_data_generator.py --schools 5 --users 30 --format sql --output test-data/sql-only/
mkdir -p test-data/sql-only

echo ""
echo "✨ All test datasets generated in test-data/ directory!"
echo ""
echo "📁 Available datasets:"
echo "   test-data/small/    - 3 schools, 20 users"
echo "   test-data/medium/   - 5 schools, 50 users"
echo "   test-data/large/    - 10 schools, 100 users"
echo "   test-data/csv-only/ - CSV format only"
echo "   test-data/sql-only/ - SQL format only"
