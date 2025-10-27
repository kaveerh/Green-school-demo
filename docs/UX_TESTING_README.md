# UX Testing Documentation

## Overview

This directory contains comprehensive UX testing documentation and automated test suites for the Green School Management System. All 15 features are tested with visual documentation through screenshots.

## Quick Start

### Prerequisites
1. **Frontend running:** `cd frontend && npm run dev` (http://localhost:3000)
2. **Backend running:** `cd backend && python main.py` (http://localhost:8000)
3. **Playwright installed:** `npm install` (in project root)

### Run All UX Tests
```bash
# From project root
./run-ux-tests.sh
```

This will:
- ✅ Check if frontend/backend are running
- ✅ Clean previous test results
- ✅ Run all UX tests with Playwright
- ✅ Capture screenshots for all features
- ✅ Generate HTML and JSON reports
- ✅ Open the HTML report in your browser

### Run Specific Feature Tests
```bash
# Test only Users feature
npx playwright test tests/ux-comprehensive.spec.ts -g "01. Users"

# Test only responsive design
npx playwright test tests/ux-comprehensive.spec.ts -g "Responsive"

# Test specific feature
npx playwright test tests/ux-comprehensive.spec.ts -g "Teachers"
```

## Documentation Structure

```
docs/
├── UX_TESTING_README.md          # This file
├── UX_TEST_PLAN.md               # Comprehensive test plan
├── UX_TEST_REPORT_TEMPLATE.md    # Report template
└── UX_TEST_REPORT.md             # Generated after testing
```

## Test Results Structure

```
test-results/
├── screenshots/                   # All screenshots organized by feature
│   ├── 00-navigation/            # Dashboard and navigation
│   ├── 01-users/                 # Users feature screenshots
│   ├── 02-schools/               # Schools feature screenshots
│   ├── 03-teachers/              # Teachers feature screenshots
│   ├── 04-students/              # Students feature screenshots
│   ├── 05-parents/               # Parents feature screenshots
│   ├── 06-subjects/              # Subjects feature screenshots
│   ├── 07-rooms/                 # Rooms feature screenshots
│   ├── 08-classes/               # Classes feature screenshots
│   ├── 09-lessons/               # Lessons feature screenshots
│   ├── 10-assessments/           # Assessments feature screenshots
│   ├── 11-attendance/            # Attendance feature screenshots
│   ├── 12-events/                # Events feature screenshots
│   ├── 13-activities/            # Activities feature screenshots
│   ├── 14-vendors/               # Vendors feature screenshots
│   └── 15-merits/                # Merits feature screenshots
├── html/                          # HTML test report
│   └── index.html                # Open this in browser
├── results.json                   # JSON test results
└── videos/                        # Videos of failed tests
```

## Features Tested

### ✅ Phase 1: Foundation (Features 1-2)
1. **Users** - Multi-persona authentication system
   - List view, Create, Edit, Delete, Responsive design
2. **Schools** - Multi-tenant foundation
   - List view, Create, Edit, Delete, Responsive design

### ✅ Phase 2: Core Entities (Features 3-5)
3. **Teachers** - Teacher management and assignments
4. **Students** - Student profiles and grade management
5. **Parents** - Parent profiles and child relationships

### ✅ Phase 3: Academic Structure (Features 6-8)
6. **Subjects** - Curriculum management
7. **Rooms** - Facility and resource management
8. **Classes** - Class creation and enrollment

### ✅ Phase 4: Academic Operations (Features 9-11)
9. **Lessons** - Lesson planning
10. **Assessments** - Grading and evaluation
11. **Attendance** - Attendance tracking

### ✅ Phase 5: Extended Features (Features 12-15)
12. **Events** - School calendar
13. **Activities** - Extracurricular activities
14. **Vendors** - Vendor management
15. **Merits** - Student reward system

## Test Scenarios

For each feature, the following scenarios are tested:

### 📋 List View Tests
- Empty state display
- Data loading and display
- Pagination controls
- Search functionality
- Filter options
- Sort capabilities

### ✏️ Create Form Tests
- Form accessibility
- Field validation (required fields)
- Field validation (format checks)
- Error message display
- Success message display
- Form submission

### 📝 Edit Form Tests
- Pre-populated data display
- Field modifications
- Validation on update
- Save changes
- Discard changes

### 👁️ Detail View Tests
- Data display completeness
- Related data display
- Action buttons availability
- Navigation to edit

### 🗑️ Delete Tests
- Delete confirmation modal
- Soft delete execution
- Success feedback
- List update after delete

### 📱 Responsive Design Tests
- Desktop view (1920x1080)
- Tablet view (768x1024)
- Mobile view (375x667)
- Layout adjustments
- Touch-friendly controls

### 🧭 Navigation Tests
- Sidebar navigation
- Breadcrumb navigation
- Back button functionality
- Deep linking

## Screenshot Naming Convention

Screenshots follow this naming pattern:
```
{sequence}-{description}.png

Examples:
01-list-view.png
02-create-form.png
03-responsive-desktop.png
04-responsive-tablet.png
05-responsive-mobile.png
```

## Viewing Test Results

### HTML Report
```bash
# Open HTML report
open test-results/html/index.html

# Or on Linux
xdg-open test-results/html/index.html
```

The HTML report includes:
- Test execution summary
- Pass/fail status for each test
- Screenshots for each test
- Videos of failed tests
- Execution timeline
- Error details

### Screenshots
```bash
# View all screenshots
ls -R test-results/screenshots/

# View specific feature screenshots
ls test-results/screenshots/01-users/

# Open screenshot directory
open test-results/screenshots/
```

### JSON Report
```bash
# View JSON results
cat test-results/results.json | jq

# Extract specific data
cat test-results/results.json | jq '.suites[].specs[].title'
```

## Troubleshooting

### Frontend Not Running
```bash
cd frontend
npm install
npm run dev
```

### Backend Not Running
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Playwright Not Installed
```bash
npm install
npx playwright install
```

### Tests Failing
1. Check if frontend is accessible: http://localhost:3000
2. Check if backend is accessible: http://localhost:8000
3. Check browser console for errors
4. Review test-results/html/index.html for details
5. Check videos in test-results/ for failed tests

### Screenshots Not Captured
1. Ensure test-results/screenshots/ directory exists
2. Check write permissions
3. Verify Playwright screenshot configuration
4. Check test execution logs

## Advanced Usage

### Run Tests in Different Browsers
```bash
# Run in Firefox
npx playwright test --project=firefox tests/ux-comprehensive.spec.ts

# Run in WebKit (Safari)
npx playwright test --project=webkit tests/ux-comprehensive.spec.ts

# Run in all browsers
npx playwright test --project=chromium --project=firefox --project=webkit
```

### Run Tests in Headed Mode (See Browser)
```bash
npx playwright test --headed tests/ux-comprehensive.spec.ts
```

### Debug Specific Test
```bash
npx playwright test --debug tests/ux-comprehensive.spec.ts -g "Users - List View"
```

### Generate Trace for Debugging
```bash
npx playwright test --trace on tests/ux-comprehensive.spec.ts
npx playwright show-trace test-results/trace.zip
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: UX Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npx playwright install --with-deps
      - run: npm run dev &
      - run: ./run-ux-tests.sh
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## Best Practices

### Before Running Tests
1. ✅ Ensure frontend and backend are running
2. ✅ Clear browser cache
3. ✅ Use consistent test data
4. ✅ Check network connectivity
5. ✅ Close unnecessary applications

### During Testing
1. ✅ Don't interact with the browser
2. ✅ Let tests complete fully
3. ✅ Monitor console for errors
4. ✅ Check test progress in terminal

### After Testing
1. ✅ Review HTML report
2. ✅ Check all screenshots
3. ✅ Document any issues found
4. ✅ Update test report
5. ✅ Share results with team

## Reporting Issues

When reporting UX issues found during testing:

```markdown
**Feature:** {feature-name}
**Severity:** Critical | High | Medium | Low
**Type:** Bug | UX Issue | Performance | Accessibility
**Description:** {detailed description}
**Steps to Reproduce:**
1. {step 1}
2. {step 2}
3. {step 3}
**Expected:** {expected behavior}
**Actual:** {actual behavior}
**Screenshot:** test-results/screenshots/{path}
**Browser:** Chromium {version}
**Viewport:** {viewport size}
```

## Performance Metrics

Tests automatically capture:
- Page load times
- Network requests
- Console errors
- Failed requests
- Slow operations

Review these in the HTML report under "Performance" section.

## Accessibility Testing

While not fully automated, manual checks should include:
- ✅ Keyboard navigation
- ✅ Screen reader compatibility
- ✅ Color contrast
- ✅ Focus indicators
- ✅ ARIA labels
- ✅ Alt text for images

## Next Steps

1. **Run Initial Tests**
   ```bash
   ./run-ux-tests.sh
   ```

2. **Review Results**
   - Open HTML report
   - Check screenshots
   - Note any issues

3. **Generate Report**
   - Use UX_TEST_REPORT_TEMPLATE.md
   - Fill in actual results
   - Add screenshots references
   - Document issues

4. **Share Results**
   - Commit test results
   - Share report with team
   - Create issues for bugs
   - Plan improvements

## Support

For questions or issues with UX testing:
1. Check this README
2. Review UX_TEST_PLAN.md
3. Check Playwright documentation
4. Contact the development team

---

**Last Updated:** 2025-10-27  
**Version:** 1.0  
**Maintained by:** UX Testing Team
