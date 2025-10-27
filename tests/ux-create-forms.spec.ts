import { test, expect, type Page } from '@playwright/test';
import { mkdir } from 'fs/promises';
import { join } from 'path';

const BASE_URL = 'http://localhost:3000';
const SCREENSHOT_DIR = 'test-results/screenshots';

async function captureScreenshot(page: Page, feature: string, name: string) {
  const dir = join(SCREENSHOT_DIR, feature);
  await mkdir(dir, { recursive: true });
  await page.screenshot({ path: join(dir, `${name}.png`), fullPage: true });
  console.log(`📸 ${feature}/${name}.png`);
}

async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
}

test.describe('CREATE Form Tests - All Features', () => {

  test('01. Schools - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/schools/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '02-schools', 'create-01-empty-form');

    // Fill form using label-based selectors
    await page.getByLabel('School Name *').fill('Green Valley Primary School');
    await page.getByLabel('Email').fill('info@greenvalley.edu');
    await page.getByLabel('Phone').fill('+1-555-0100');
    await page.getByLabel('Address Line 1').fill('123 Education Street');
    await page.getByLabel('City').fill('Springfield');
    
    await captureScreenshot(page, '02-schools', 'create-02-filled-form');

    // Submit
    await page.getByRole('button', { name: 'Create School' }).click();
    await waitForPageLoad(page);
    await captureScreenshot(page, '02-schools', 'create-03-after-submit');
  });

  test('02. Teachers - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/teachers/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '03-teachers', 'create-01-empty-form');

    // Fill form - fill any visible required fields
    const inputs = await page.locator('input[type="text"], input[type="date"]').all();
    if (inputs.length > 0) await inputs[0].fill('TCH001');
    if (inputs.length > 1) await inputs[1].fill('2024-01-15');
    
    await captureScreenshot(page, '03-teachers', 'create-02-filled-form');

    const submitBtn = page.getByRole('button', { name: /create|submit/i });
    if (await submitBtn.isVisible()) await submitBtn.click();
    await waitForPageLoad(page);
    await captureScreenshot(page, '03-teachers', 'create-03-after-submit');
  });

  test('03. Students - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/students/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '04-students', 'create-01-empty-form');

    // Fill form using label-based selectors
    await page.getByLabel('Student ID *').fill('STU2024001');
    await page.getByLabel('Grade Level *').selectOption('3');
    await page.getByLabel('Date of Birth *').fill('2015-03-20');
    await page.getByLabel('Enrollment Date *').fill('2024-09-01');
    await page.getByLabel('Contact Name').fill('Mary Wilson');
    await page.getByLabel('Contact Phone').fill('+1-555-0201');
    
    await captureScreenshot(page, '04-students', 'create-02-filled-form');

    await page.getByRole('button', { name: 'Create Student' }).click();
    await waitForPageLoad(page);
    await captureScreenshot(page, '04-students', 'create-03-after-submit');
  });

  test('04. Parents - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/parents/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '05-parents', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="occupation"]', 'Software Engineer');
    await page.fill('input[name="employer"]', 'Tech Corp');
    await page.fill('input[name="work_phone"]', '+1-555-0301');
    await page.selectOption('select[name="relationship"]', 'mother');
    
    await captureScreenshot(page, '05-parents', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '05-parents', 'create-03-after-submit');
  });

  test('05. Subjects - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/subjects/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '06-subjects', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="name"]', 'Mathematics');
    await page.fill('input[name="code"]', 'MATH101');
    await page.fill('input[name="description"]', 'Basic Mathematics for Grade 3');
    await page.selectOption('select[name="grade"]', '3');
    await page.fill('input[name="credits"]', '4');
    
    await captureScreenshot(page, '06-subjects', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '06-subjects', 'create-03-after-submit');
  });

  test('06. Rooms - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/rooms/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '07-rooms', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="room_number"]', '101');
    await page.fill('input[name="room_name"]', 'Science Lab A');
    await page.selectOption('select[name="room_type"]', 'laboratory');
    await page.fill('input[name="building"]', 'Main Building');
    await page.fill('input[name="capacity"]', '30');
    
    await captureScreenshot(page, '07-rooms', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '07-rooms', 'create-03-after-submit');
  });

  test('07. Classes - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/classes/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '08-classes', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="name"]', 'Grade 3A');
    await page.selectOption('select[name="grade"]', '3');
    await page.fill('input[name="section"]', 'A');
    await page.fill('input[name="academic_year"]', '2024-2025');
    await page.fill('input[name="max_students"]', '30');
    
    await captureScreenshot(page, '08-classes', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '08-classes', 'create-03-after-submit');
  });

  test('08. Lessons - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/lessons/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '09-lessons', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="title"]', 'Introduction to Fractions');
    await page.fill('input[name="lesson_date"]', '2024-11-01');
    await page.fill('input[name="start_time"]', '09:00');
    await page.fill('input[name="end_time"]', '10:00');
    await page.fill('textarea[name="description"]', 'Basic concepts of fractions');
    
    await captureScreenshot(page, '09-lessons', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '09-lessons', 'create-03-after-submit');
  });

  test('09. Assessments - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/assessments/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '10-assessments', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="title"]', 'Math Quiz - Fractions');
    await page.selectOption('select[name="assessment_type"]', 'quiz');
    await page.fill('input[name="assessment_date"]', '2024-11-15');
    await page.fill('input[name="total_marks"]', '100');
    await page.fill('input[name="passing_marks"]', '40');
    await page.selectOption('select[name="quarter"]', 'Q1');
    
    await captureScreenshot(page, '10-assessments', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '10-assessments', 'create-03-after-submit');
  });

  test('10. Attendance - Mark with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/attendance/mark`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '11-attendance', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="attendance_date"]', '2024-10-27');
    
    await captureScreenshot(page, '11-attendance', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '11-attendance', 'create-03-after-submit');
  });

  test('11. Events - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/events/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '12-events', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="title"]', 'Annual Sports Day');
    await page.selectOption('select[name="event_type"]', 'sports');
    await page.fill('input[name="event_date"]', '2024-12-15');
    await page.fill('input[name="start_time"]', '08:00');
    await page.fill('input[name="end_time"]', '16:00');
    await page.fill('input[name="location"]', 'School Playground');
    
    await captureScreenshot(page, '12-events', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '12-events', 'create-03-after-submit');
  });

  test('12. Activities - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/activities/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '13-activities', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="name"]', 'Chess Club');
    await page.selectOption('select[name="activity_type"]', 'club');
    await page.fill('textarea[name="description"]', 'Learn and play chess');
    await page.fill('input[name="instructor_name"]', 'Mr. Robert Brown');
    await page.fill('input[name="max_participants"]', '20');
    await page.fill('input[name="fee"]', '50.00');
    
    await captureScreenshot(page, '13-activities', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '13-activities', 'create-03-after-submit');
  });

  test('13. Vendors - Create with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/vendors/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '14-vendors', 'create-01-empty-form');

    // Fill form
    await page.fill('input[name="name"]', 'ABC Stationery Supplies');
    await page.fill('input[name="vendor_code"]', 'VEN001');
    await page.selectOption('select[name="vendor_type"]', 'supplier');
    await page.fill('input[name="contact_person"]', 'Michael Chen');
    await page.fill('input[name="email"]', 'michael@abcstationery.com');
    await page.fill('input[name="phone"]', '+1-555-0400');
    
    await captureScreenshot(page, '14-vendors', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '14-vendors', 'create-03-after-submit');
  });

  test('14. Merits - Award with Sample Data', async ({ page }) => {
    await page.goto(`${BASE_URL}/merits/award`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '15-merits', 'create-01-empty-form');

    // Fill form
    await page.selectOption('select[name="merit_type"]', 'academic_excellence');
    await page.fill('input[name="points"]', '10');
    await page.fill('textarea[name="reason"]', 'Excellent performance in Math Quiz');
    await page.fill('input[name="awarded_date"]', '2024-10-27');
    await page.selectOption('select[name="quarter"]', 'Q1');
    
    await captureScreenshot(page, '15-merits', 'create-02-filled-form');

    await page.click('button[type="submit"]');
    await waitForPageLoad(page);
    await captureScreenshot(page, '15-merits', 'create-03-after-submit');
  });
});
