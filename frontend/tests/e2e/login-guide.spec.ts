import { test, expect } from '@playwright/test'
import { chromium } from '@playwright/test'

/**
 * Login Guide Test Suite
 * Captures screenshots and recordings for login documentation
 * for different user personas: Administrator, Teacher, Student, Parent
 */

// Test data for different user types
const users = {
  administrator: {
    email: 'admin@greenschool.edu',
    password: 'Admin123',
    persona: 'administrator',
    name: 'Admin User',
    expectedMenuItems: ['Dashboard', 'Users', 'Schools', 'Teachers', 'Students', 'Parents', 'Subjects', 'Rooms', 'Classes', 'Lessons', 'Assessments', 'Attendance', 'Events', 'Activities', 'Vendors', 'Merits']
  },
  teacher: {
    email: 'teacher@greenschool.edu',
    password: 'Admin123',
    persona: 'teacher',
    name: 'Teacher User',
    expectedMenuItems: ['Dashboard', 'Students', 'Parents', 'Subjects', 'Rooms', 'Classes', 'Lessons', 'Assessments', 'Attendance', 'Events', 'Activities', 'Merits']
  },
  student: {
    email: 'student@greenschool.edu',
    password: 'Admin123',
    persona: 'student',
    name: 'Student User',
    expectedMenuItems: ['Dashboard', 'Classes', 'Assessments', 'Attendance', 'Events', 'Activities', 'Merits']
  },
  parent: {
    email: 'parent@greenschool.edu',
    password: 'Admin123',
    persona: 'parent',
    name: 'Parent User',
    expectedMenuItems: ['Dashboard', 'Classes', 'Assessments', 'Attendance', 'Events', 'Activities', 'Merits']
  }
}

// Configure test to run serially and with video recording
test.describe.configure({ mode: 'serial' })

test.use({
  video: 'on',
  screenshot: 'on'
})

test.describe('Login Guide - All User Types', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('http://localhost:3000')
    await page.waitForLoadState('networkidle')
  })

  test('1. Administrator Login Flow', async ({ page }) => {
    const user = users.administrator

    // Step 1: Home page
    await page.screenshot({
      path: 'docs/login/screenshots/admin-01-home.png',
      fullPage: true
    })

    // Step 2: Click Sign In
    await page.getByRole('link', { name: 'Sign In' }).click()
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/admin-02-login-page.png',
      fullPage: true
    })

    // Step 3: Click "Sign in with Keycloak"
    await page.getByRole('button', { name: /Sign in with Keycloak/i }).click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    // Check if we're on Keycloak login page
    await expect(page).toHaveURL(/localhost:8080/)
    await page.screenshot({
      path: 'docs/login/screenshots/admin-03-keycloak-login.png',
      fullPage: true
    })

    // Step 4: Enter credentials
    await page.fill('input[name="username"]', user.email)
    await page.screenshot({
      path: 'docs/login/screenshots/admin-04-enter-email.png',
      fullPage: true
    })

    await page.fill('input[name="password"]', user.password)
    await page.screenshot({
      path: 'docs/login/screenshots/admin-05-enter-password.png',
      fullPage: true
    })

    // Step 5: Click Sign In
    await page.click('input[type="submit"]')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    // Should be redirected to dashboard
    await expect(page).toHaveURL(/localhost:3000\/dashboard/)
    await page.screenshot({
      path: 'docs/login/screenshots/admin-06-dashboard.png',
      fullPage: true
    })

    // Step 6: Show navigation menu
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/admin-07-navigation.png',
      fullPage: true
    })

    // Step 7: Show user menu
    await page.click('.user-button')
    await page.waitForTimeout(500)
    await page.screenshot({
      path: 'docs/login/screenshots/admin-08-user-menu.png',
      fullPage: true
    })

    console.log('✅ Administrator login flow captured')
  })

  test('2. Teacher Login Flow', async ({ page }) => {
    const user = users.teacher

    // Step 1: Home page
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-01-home.png',
      fullPage: true
    })

    // Step 2: Click Sign In
    await page.getByRole('link', { name: 'Sign In' }).click()
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-02-login-page.png',
      fullPage: true
    })

    // Step 3: Click "Sign in with Keycloak"
    await page.getByRole('button', { name: /Sign in with Keycloak/i }).click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await expect(page).toHaveURL(/localhost:8080/)
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-03-keycloak-login.png',
      fullPage: true
    })

    // Step 4: Enter credentials
    await page.fill('input[name="username"]', user.email)
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-04-enter-email.png',
      fullPage: true
    })

    await page.fill('input[name="password"]', user.password)
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-05-enter-password.png',
      fullPage: true
    })

    // Step 5: Click Sign In
    await page.click('input[type="submit"]')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    await expect(page).toHaveURL(/localhost:3000\/dashboard/)
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-06-dashboard.png',
      fullPage: true
    })

    // Step 6: Show navigation menu
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-07-navigation.png',
      fullPage: true
    })

    // Step 7: Show user menu
    await page.click('.user-button')
    await page.waitForTimeout(500)
    await page.screenshot({
      path: 'docs/login/screenshots/teacher-08-user-menu.png',
      fullPage: true
    })

    console.log('✅ Teacher login flow captured')
  })

  test('3. Student Login Flow', async ({ page }) => {
    const user = users.student

    // Step 1: Home page
    await page.screenshot({
      path: 'docs/login/screenshots/student-01-home.png',
      fullPage: true
    })

    // Step 2: Click Sign In
    await page.getByRole('link', { name: 'Sign In' }).click()
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/student-02-login-page.png',
      fullPage: true
    })

    // Step 3: Click "Sign in with Keycloak"
    await page.getByRole('button', { name: /Sign in with Keycloak/i }).click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await expect(page).toHaveURL(/localhost:8080/)
    await page.screenshot({
      path: 'docs/login/screenshots/student-03-keycloak-login.png',
      fullPage: true
    })

    // Step 4: Enter credentials
    await page.fill('input[name="username"]', user.email)
    await page.screenshot({
      path: 'docs/login/screenshots/student-04-enter-email.png',
      fullPage: true
    })

    await page.fill('input[name="password"]', user.password)
    await page.screenshot({
      path: 'docs/login/screenshots/student-05-enter-password.png',
      fullPage: true
    })

    // Step 5: Click Sign In
    await page.click('input[type="submit"]')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    await expect(page).toHaveURL(/localhost:3000\/dashboard/)
    await page.screenshot({
      path: 'docs/login/screenshots/student-06-dashboard.png',
      fullPage: true
    })

    // Step 6: Show navigation menu (limited items for student)
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/student-07-navigation.png',
      fullPage: true
    })

    // Step 7: Show user menu
    await page.click('.user-button')
    await page.waitForTimeout(500)
    await page.screenshot({
      path: 'docs/login/screenshots/student-08-user-menu.png',
      fullPage: true
    })

    console.log('✅ Student login flow captured')
  })

  test('4. Parent Login Flow', async ({ page }) => {
    const user = users.parent

    // Step 1: Home page
    await page.screenshot({
      path: 'docs/login/screenshots/parent-01-home.png',
      fullPage: true
    })

    // Step 2: Click Sign In
    await page.getByRole('link', { name: 'Sign In' }).click()
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/parent-02-login-page.png',
      fullPage: true
    })

    // Step 3: Click "Sign in with Keycloak"
    await page.getByRole('button', { name: /Sign in with Keycloak/i }).click()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await expect(page).toHaveURL(/localhost:8080/)
    await page.screenshot({
      path: 'docs/login/screenshots/parent-03-keycloak-login.png',
      fullPage: true
    })

    // Step 4: Enter credentials
    await page.fill('input[name="username"]', user.email)
    await page.screenshot({
      path: 'docs/login/screenshots/parent-04-enter-email.png',
      fullPage: true
    })

    await page.fill('input[name="password"]', user.password)
    await page.screenshot({
      path: 'docs/login/screenshots/parent-05-enter-password.png',
      fullPage: true
    })

    // Step 5: Click Sign In
    await page.click('input[type="submit"]')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    await expect(page).toHaveURL(/localhost:3000\/dashboard/)
    await page.screenshot({
      path: 'docs/login/screenshots/parent-06-dashboard.png',
      fullPage: true
    })

    // Step 6: Show navigation menu (limited items for parent)
    await page.waitForTimeout(1000)
    await page.screenshot({
      path: 'docs/login/screenshots/parent-07-navigation.png',
      fullPage: true
    })

    // Step 7: Show user menu
    await page.click('.user-button')
    await page.waitForTimeout(500)
    await page.screenshot({
      path: 'docs/login/screenshots/parent-08-user-menu.png',
      fullPage: true
    })

    console.log('✅ Parent login flow captured')
  })
})

test.describe('Demo Page Screenshots', () => {
  test('Capture Demo Page', async ({ page }) => {
    await page.goto('http://localhost:3000/demo')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)

    await page.screenshot({
      path: 'docs/login/screenshots/demo-page.png',
      fullPage: true
    })

    console.log('✅ Demo page captured')
  })
})
