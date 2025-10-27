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

async function fillFirstInputs(page: Page, values: string[]) {
  const inputs = await page.locator('input[type="text"]:visible, input[type="email"]:visible, input[type="date"]:visible, input[type="number"]:visible').all();
  for (let i = 0; i < Math.min(inputs.length, values.length); i++) {
    try {
      await inputs[i].fill(values[i]);
    } catch (e) {
      // Skip if field is not fillable
    }
  }
}

test.describe('CREATE Form Tests - Simplified', () => {

  test('Schools - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/schools/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '02-schools', 'create-01-empty');

    await page.getByLabel(/school name/i).fill('Green Valley Primary');
    await page.getByLabel(/email/i).fill('info@greenvalley.edu');
    await page.getByLabel(/phone/i).fill('+1-555-0100');
    
    await captureScreenshot(page, '02-schools', 'create-02-filled');
    await page.getByRole('button', { name: /create school/i }).click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '02-schools', 'create-03-submitted');
  });

  test('Teachers - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/teachers/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '03-teachers', 'create-01-empty');
    
    await fillFirstInputs(page, ['TCH001', '2024-01-15', 'Mathematics']);
    
    await captureScreenshot(page, '03-teachers', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '03-teachers', 'create-03-submitted');
  });

  test('Students - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/students/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '04-students', 'create-01-empty');

    await page.getByLabel(/student id/i).fill('STU2024001');
    await page.getByLabel(/date of birth/i).fill('2015-03-20');
    await page.getByLabel(/enrollment date/i).fill('2024-09-01');
    await page.getByLabel(/grade/i).selectOption('3');
    
    await captureScreenshot(page, '04-students', 'create-02-filled');
    await page.getByRole('button', { name: /create student/i }).click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '04-students', 'create-03-submitted');
  });

  test('Parents - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/parents/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '05-parents', 'create-01-empty');
    
    await fillFirstInputs(page, ['Software Engineer', 'Tech Corp', '+1-555-0301']);
    
    await captureScreenshot(page, '05-parents', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '05-parents', 'create-03-submitted');
  });

  test('Subjects - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/subjects/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '06-subjects', 'create-01-empty');
    
    await fillFirstInputs(page, ['Mathematics', 'MATH101', 'Basic Math']);
    
    await captureScreenshot(page, '06-subjects', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '06-subjects', 'create-03-submitted');
  });

  test('Rooms - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/rooms/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '07-rooms', 'create-01-empty');
    
    await fillFirstInputs(page, ['101', 'Science Lab A', 'Main Building', '30']);
    
    await captureScreenshot(page, '07-rooms', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '07-rooms', 'create-03-submitted');
  });

  test('Classes - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/classes/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '08-classes', 'create-01-empty');
    
    await fillFirstInputs(page, ['Grade 3A', 'A', '2024-2025', '30']);
    
    await captureScreenshot(page, '08-classes', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '08-classes', 'create-03-submitted');
  });

  test('Lessons - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/lessons/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '09-lessons', 'create-01-empty');
    
    await fillFirstInputs(page, ['Introduction to Fractions', '2024-11-01', '09:00', '10:00']);
    
    await captureScreenshot(page, '09-lessons', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '09-lessons', 'create-03-submitted');
  });

  test('Assessments - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/assessments/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '10-assessments', 'create-01-empty');
    
    await fillFirstInputs(page, ['Math Quiz', '2024-11-15', '100', '40']);
    
    await captureScreenshot(page, '10-assessments', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '10-assessments', 'create-03-submitted');
  });

  test('Attendance - Mark Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/attendance/mark`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '11-attendance', 'create-01-empty');
    
    await fillFirstInputs(page, ['2024-10-27']);
    
    await captureScreenshot(page, '11-attendance', 'create-02-filled');
    const btn = page.getByRole('button', { name: /mark|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '11-attendance', 'create-03-submitted');
  });

  test('Events - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/events/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '12-events', 'create-01-empty');
    
    await fillFirstInputs(page, ['Annual Sports Day', '2024-12-15', '08:00', '16:00', 'School Playground']);
    
    await captureScreenshot(page, '12-events', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '12-events', 'create-03-submitted');
  });

  test('Activities - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/activities/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '13-activities', 'create-01-empty');
    
    await fillFirstInputs(page, ['Chess Club', 'Mr. Robert Brown', '20', '50.00']);
    
    await captureScreenshot(page, '13-activities', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '13-activities', 'create-03-submitted');
  });

  test('Vendors - Create Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/vendors/create`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '14-vendors', 'create-01-empty');
    
    await fillFirstInputs(page, ['ABC Stationery', 'VEN001', 'Michael Chen', 'michael@abc.com', '+1-555-0400']);
    
    await captureScreenshot(page, '14-vendors', 'create-02-filled');
    const btn = page.getByRole('button', { name: /create|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '14-vendors', 'create-03-submitted');
  });

  test('Merits - Award Form', async ({ page }) => {
    await page.goto(`${BASE_URL}/merits/award`);
    await waitForPageLoad(page);
    await captureScreenshot(page, '15-merits', 'create-01-empty');
    
    await fillFirstInputs(page, ['10', 'Excellent performance', '2024-10-27']);
    
    await captureScreenshot(page, '15-merits', 'create-02-filled');
    const btn = page.getByRole('button', { name: /award|submit/i }).first();
    if (await btn.isVisible()) await btn.click();
    await page.waitForTimeout(2000);
    await captureScreenshot(page, '15-merits', 'create-03-submitted');
  });
});
