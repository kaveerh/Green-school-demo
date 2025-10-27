#!/bin/bash

# Green School Management System - UX Test Runner
# This script runs comprehensive UX tests and generates documentation

set -e

echo "🎯 Green School Management System - UX Testing Suite"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if frontend is running
echo -e "${BLUE}📡 Checking if frontend is running...${NC}"
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${RED}❌ Frontend is not running. Please start it with:${NC}"
    echo "   cd frontend && npm run dev"
    exit 1
fi

# Check if backend is running
echo -e "${BLUE}📡 Checking if backend is running...${NC}"
if curl -s http://localhost:8000/docs > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend is not running. Some tests may fail.${NC}"
    echo "   To start backend: cd backend && python main.py"
fi

echo ""
echo -e "${BLUE}🧹 Cleaning previous test results...${NC}"
rm -rf test-results/screenshots/*
mkdir -p test-results/screenshots

echo ""
echo -e "${BLUE}🚀 Running UX tests...${NC}"
echo ""

# Run Playwright tests
npx playwright test tests/ux-comprehensive.spec.ts \
    --reporter=html,json,list

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Some tests failed or had issues${NC}"
fi

echo ""
echo -e "${BLUE}📊 Generating test report...${NC}"

# Count screenshots
SCREENSHOT_COUNT=$(find test-results/screenshots -name "*.png" 2>/dev/null | wc -l)
echo -e "${GREEN}📸 Screenshots captured: ${SCREENSHOT_COUNT}${NC}"

# List screenshot directories
echo ""
echo -e "${BLUE}📁 Screenshot directories created:${NC}"
ls -1 test-results/screenshots/ 2>/dev/null | while read dir; do
    count=$(ls -1 test-results/screenshots/$dir/*.png 2>/dev/null | wc -l)
    echo "   - $dir ($count screenshots)"
done

echo ""
echo -e "${BLUE}📄 Test artifacts location:${NC}"
echo "   - Screenshots: test-results/screenshots/"
echo "   - HTML Report: test-results/html/index.html"
echo "   - JSON Report: test-results/results.json"
echo "   - Videos: test-results/ (for failed tests)"

echo ""
echo -e "${BLUE}🌐 Opening HTML report...${NC}"
if command -v open &> /dev/null; then
    open test-results/html/index.html
elif command -v xdg-open &> /dev/null; then
    xdg-open test-results/html/index.html
else
    echo "   Please open: test-results/html/index.html"
fi

echo ""
echo -e "${GREEN}✨ UX Testing Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review HTML report: test-results/html/index.html"
echo "2. Check screenshots: test-results/screenshots/"
echo "3. Generate final report: docs/UX_TEST_REPORT.md"
echo ""

exit $TEST_EXIT_CODE
