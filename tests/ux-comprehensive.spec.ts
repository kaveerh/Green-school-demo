import { test, expect, type Page } from '@playwright/test';
import { mkdir } from 'fs/promises';
import { join } from 'path';

// Test configuration
const BASE_URL = 'http://localhost:3000';
const SCREENSHOT_DIR = 'test-results/screenshots';
const VIEWPORTS = {
  desktop: { width: 1920, height: 1080 },
  tablet: { width: 768, height: 1024 },
  mobile: { width: 375, height: 667 }
};

// Helper to ensure screenshot directory exists
async function ensureScreenshotDir(feature: string) {
  const dir = join(SCREENSHOT_DIR, feature);
  await mkdir(dir, { recursive: true });
  return dir;
}

// Helper to take and save screenshot
async function captureScreenshot(page: Page, feature: string, name: string) {
  const dir = await ensureScreenshotDir(feature);
  const path = join(dir, `${name}.png`);
  await page.screenshot({ path, fullPage: true });
  console.log(`📸 Screenshot saved: ${path}`);
}

// Helper to wait for page load
async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500); // Additional wait for animations
}

test.describe('Green School Management System - Comprehensive UX Testing', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
  });

  // ============================================================================
  // FEATURE 01: USERS
  // ============================================================================
  test.describe('01. Users Feature', () => {
    
    test('Users - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/users`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '01-users', '01-list-view');
      
      // Check for key elements
      await expect(page.locator('h1, h2').filter({ hasText: /users/i })).toBeVisible();
    });

    test('Users - Create Form Empty', async ({ page }) => {
      await page.goto(`${BASE_URL}/users/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '01-users', '02-create-form-empty');
    });

    test('Users - Create Form Filled', async ({ page }) => {
      await page.goto(`${BASE_URL}/users/create`);
      await waitForPageLoad(page);
      
      // Fill form fields (if they exist)
      const emailInput = page.locator('input[type="email"], input[name="email"]').first();
      if (await emailInput.isVisible()) {
        await emailInput.fill('testuser@example.com');
      }
      
      await captureScreenshot(page, '01-users', '03-create-form-filled');
    });

    test('Users - Responsive Desktop', async ({ page }) => {
      await page.setViewportSize(VIEWPORTS.desktop);
      await page.goto(`${BASE_URL}/users`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '01-users', '04-responsive-desktop');
    });

    test('Users - Responsive Tablet', async ({ page }) => {
      await page.setViewportSize(VIEWPORTS.tablet);
      await page.goto(`${BASE_URL}/users`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '01-users', '05-responsive-tablet');
    });

    test('Users - Responsive Mobile', async ({ page }) => {
      await page.setViewportSize(VIEWPORTS.mobile);
      await page.goto(`${BASE_URL}/users`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '01-users', '06-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 02: SCHOOLS
  // ============================================================================
  test.describe('02. Schools Feature', () => {
    
    test('Schools - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/schools`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '02-schools', '01-list-view');
    });

    test('Schools - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/schools/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '02-schools', '02-create-form');
    });

    test('Schools - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/schools`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '02-schools', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '02-schools', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '02-schools', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 03: TEACHERS
  // ============================================================================
  test.describe('03. Teachers Feature', () => {
    
    test('Teachers - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/teachers`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '03-teachers', '01-list-view');
    });

    test('Teachers - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/teachers/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '03-teachers', '02-create-form');
    });

    test('Teachers - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/teachers`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '03-teachers', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '03-teachers', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '03-teachers', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 04: STUDENTS
  // ============================================================================
  test.describe('04. Students Feature', () => {
    
    test('Students - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/students`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '04-students', '01-list-view');
    });

    test('Students - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/students/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '04-students', '02-create-form');
    });

    test('Students - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/students`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '04-students', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '04-students', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '04-students', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 05: PARENTS
  // ============================================================================
  test.describe('05. Parents Feature', () => {
    
    test('Parents - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/parents`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '05-parents', '01-list-view');
    });

    test('Parents - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/parents/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '05-parents', '02-create-form');
    });

    test('Parents - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/parents`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '05-parents', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '05-parents', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '05-parents', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 06: SUBJECTS
  // ============================================================================
  test.describe('06. Subjects Feature', () => {
    
    test('Subjects - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/subjects`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '06-subjects', '01-list-view');
    });

    test('Subjects - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/subjects/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '06-subjects', '02-create-form');
    });

    test('Subjects - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/subjects`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '06-subjects', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '06-subjects', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '06-subjects', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 07: ROOMS
  // ============================================================================
  test.describe('07. Rooms Feature', () => {
    
    test('Rooms - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/rooms`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '07-rooms', '01-list-view');
    });

    test('Rooms - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/rooms/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '07-rooms', '02-create-form');
    });

    test('Rooms - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/rooms`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '07-rooms', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '07-rooms', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '07-rooms', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 08: CLASSES
  // ============================================================================
  test.describe('08. Classes Feature', () => {
    
    test('Classes - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/classes`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '08-classes', '01-list-view');
    });

    test('Classes - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/classes/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '08-classes', '02-create-form');
    });

    test('Classes - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/classes`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '08-classes', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '08-classes', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '08-classes', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 09: LESSONS
  // ============================================================================
  test.describe('09. Lessons Feature', () => {
    
    test('Lessons - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/lessons`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '09-lessons', '01-list-view');
    });

    test('Lessons - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/lessons/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '09-lessons', '02-create-form');
    });

    test('Lessons - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/lessons`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '09-lessons', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '09-lessons', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '09-lessons', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 10: ASSESSMENTS
  // ============================================================================
  test.describe('10. Assessments Feature', () => {
    
    test('Assessments - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/assessments`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '10-assessments', '01-list-view');
    });

    test('Assessments - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/assessments/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '10-assessments', '02-create-form');
    });

    test('Assessments - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/assessments`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '10-assessments', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '10-assessments', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '10-assessments', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 11: ATTENDANCE
  // ============================================================================
  test.describe('11. Attendance Feature', () => {
    
    test('Attendance - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/attendance`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '11-attendance', '01-list-view');
    });

    test('Attendance - Mark Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/attendance/mark`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '11-attendance', '02-mark-form');
    });

    test('Attendance - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/attendance`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '11-attendance', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '11-attendance', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '11-attendance', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 12: EVENTS
  // ============================================================================
  test.describe('12. Events Feature', () => {
    
    test('Events - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/events`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '12-events', '01-list-view');
    });

    test('Events - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/events/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '12-events', '02-create-form');
    });

    test('Events - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/events`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '12-events', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '12-events', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '12-events', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 13: ACTIVITIES
  // ============================================================================
  test.describe('13. Activities Feature', () => {
    
    test('Activities - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/activities`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '13-activities', '01-list-view');
    });

    test('Activities - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/activities/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '13-activities', '02-create-form');
    });

    test('Activities - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/activities`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '13-activities', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '13-activities', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '13-activities', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 14: VENDORS
  // ============================================================================
  test.describe('14. Vendors Feature', () => {
    
    test('Vendors - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/vendors`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '14-vendors', '01-list-view');
    });

    test('Vendors - Create Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/vendors/create`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '14-vendors', '02-create-form');
    });

    test('Vendors - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/vendors`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '14-vendors', '03-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '14-vendors', '04-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '14-vendors', '05-responsive-mobile');
    });
  });

  // ============================================================================
  // FEATURE 15: MERITS
  // ============================================================================
  test.describe('15. Merits Feature', () => {
    
    test('Merits - List View', async ({ page }) => {
      await page.goto(`${BASE_URL}/merits`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '15-merits', '01-list-view');
    });

    test('Merits - Award Form', async ({ page }) => {
      await page.goto(`${BASE_URL}/merits/award`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '15-merits', '02-award-form');
    });

    test('Merits - Leaderboard', async ({ page }) => {
      await page.goto(`${BASE_URL}/merits/leaderboard`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '15-merits', '03-leaderboard');
    });

    test('Merits - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/merits`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '15-merits', '04-responsive-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '15-merits', '05-responsive-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '15-merits', '06-responsive-mobile');
    });
  });

  // ============================================================================
  // NAVIGATION & DASHBOARD TESTS
  // ============================================================================
  test.describe('Navigation & Dashboard', () => {
    
    test('Dashboard - Main View', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForPageLoad(page);
      await captureScreenshot(page, '00-navigation', '01-dashboard');
    });

    test('Dashboard - Responsive Views', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);
      
      await page.setViewportSize(VIEWPORTS.desktop);
      await waitForPageLoad(page);
      await captureScreenshot(page, '00-navigation', '02-dashboard-desktop');
      
      await page.setViewportSize(VIEWPORTS.tablet);
      await waitForPageLoad(page);
      await captureScreenshot(page, '00-navigation', '03-dashboard-tablet');
      
      await page.setViewportSize(VIEWPORTS.mobile);
      await waitForPageLoad(page);
      await captureScreenshot(page, '00-navigation', '04-dashboard-mobile');
    });

    test('Navigation - Sidebar Menu', async ({ page }) => {
      await page.goto(`${BASE_URL}/dashboard`);
      await waitForPageLoad(page);
      
      // Try to capture sidebar if visible
      const sidebar = page.locator('nav, aside, [role="navigation"]').first();
      if (await sidebar.isVisible()) {
        await captureScreenshot(page, '00-navigation', '05-sidebar-menu');
      }
    });
  });
});
