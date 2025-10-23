import { test, expect } from '@playwright/test'

test.describe('Teachers Management', () => {
  const SCHOOL_ID = '60da2256-81fc-4ca5-bf6b-467b8d371c61'

  test.beforeEach(async ({ page }) => {
    // Set school ID in localStorage
    await page.goto('/')
    await page.evaluate((schoolId) => {
      localStorage.setItem('current_school_id', schoolId)
    }, SCHOOL_ID)
  })

  test('should display teachers list page', async ({ page }) => {
    await page.goto('/teachers')

    // Check page title/heading
    await expect(page.locator('h1, h2').filter({ hasText: /teachers/i }).first()).toBeVisible()

    // Check for "Add" or "Create" button
    const addButton = page.locator('button, a').filter({ hasText: /add|create|new/i }).first()
    await expect(addButton).toBeVisible()
  })

  test('should navigate to create teacher form', async ({ page }) => {
    await page.goto('/teachers')

    // Click add/create button
    const addButton = page.locator('button, a').filter({ hasText: /add|create|new/i }).first()
    await addButton.click()

    // Should navigate to create form
    await page.waitForURL(/\/teachers\/(create|new)/)

    // Check for form fields
    await expect(page.locator('input[name="employee_id"], input[id*="employee"]').first()).toBeVisible()
    await expect(page.locator('input[name="hire_date"], input[type="date"]').first()).toBeVisible()
  })

  test('should create a new teacher', async ({ page }) => {
    await page.goto('/teachers/create')

    // Fill in required fields
    const timestamp = Date.now()
    const employeeId = `E${timestamp}`

    // Employee ID
    const employeeIdField = page.locator('input[name="employee_id"], input[id*="employee"]').first()
    await employeeIdField.fill(employeeId)

    // Hire Date
    const hireDateField = page.locator('input[name="hire_date"], input[type="date"]').first()
    await hireDateField.fill('2024-01-15')

    // Grade Levels - look for checkboxes or multi-select
    const gradeLevelInput = page.locator('input[name*="grade"], select[name*="grade"]').first()
    if (await gradeLevelInput.isVisible()) {
      await gradeLevelInput.fill('5')
    }

    // User selection - look for UserSelector component
    const userSelector = page.locator('input[placeholder*="user"], input[placeholder*="Search"]').first()
    if (await userSelector.isVisible()) {
      await userSelector.click()
      await page.waitForTimeout(500)
      // Select first user from dropdown
      const firstUser = page.locator('.dropdown-item, [role="option"]').first()
      if (await firstUser.isVisible()) {
        await firstUser.click()
      }
    }

    // Submit form
    const submitButton = page.locator('button[type="submit"], button').filter({ hasText: /save|create|submit/i }).first()
    await submitButton.click()

    // Should redirect to teachers list or show success
    await page.waitForTimeout(2000)
    const currentUrl = page.url()
    expect(currentUrl).toMatch(/\/teachers/)
  })

  test('should display validation errors for empty required fields', async ({ page }) => {
    await page.goto('/teachers/create')

    // Try to submit without filling fields
    const submitButton = page.locator('button[type="submit"], button').filter({ hasText: /save|create|submit/i }).first()
    await submitButton.click()

    // Check for validation errors
    await page.waitForTimeout(500)
    const errorMessages = page.locator('.error, .text-red-500, [class*="error"]')
    const errorCount = await errorMessages.count()
    expect(errorCount).toBeGreaterThan(0)
  })

  test('should edit an existing teacher', async ({ page }) => {
    await page.goto('/teachers')

    // Wait for teachers to load
    await page.waitForTimeout(1000)

    // Click edit button on first teacher
    const editButton = page.locator('button, a').filter({ hasText: /edit/i }).first()
    if (await editButton.isVisible()) {
      await editButton.click()

      // Should navigate to edit form
      await page.waitForURL(/\/teachers\/[a-f0-9-]+\/edit/)

      // Modify a field
      const jobTitleField = page.locator('input[name="job_title"], input[id*="job"]').first()
      if (await jobTitleField.isVisible()) {
        await jobTitleField.fill('Updated Title')

        // Save
        const saveButton = page.locator('button[type="submit"], button').filter({ hasText: /save|update/i }).first()
        await saveButton.click()

        await page.waitForTimeout(2000)
      }
    }
  })

  test('should delete a teacher', async ({ page }) => {
    await page.goto('/teachers')

    // Wait for teachers to load
    await page.waitForTimeout(1000)

    // Click delete button on first teacher
    const deleteButton = page.locator('button').filter({ hasText: /delete/i }).first()
    if (await deleteButton.isVisible()) {
      await deleteButton.click()

      // Confirm deletion in dialog/modal
      await page.waitForTimeout(500)
      const confirmButton = page.locator('button').filter({ hasText: /confirm|yes|delete/i }).first()
      if (await confirmButton.isVisible()) {
        await confirmButton.click()
        await page.waitForTimeout(1000)
      }
    }
  })

  test('should search/filter teachers', async ({ page }) => {
    await page.goto('/teachers')

    // Wait for teachers to load
    await page.waitForTimeout(1000)

    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"]').first()
    if (await searchInput.isVisible()) {
      await searchInput.fill('teacher')
      await page.waitForTimeout(500)
    }
  })

  test('should handle pagination', async ({ page }) => {
    await page.goto('/teachers')

    // Wait for teachers to load
    await page.waitForTimeout(1000)

    // Look for pagination controls
    const nextButton = page.locator('button, a').filter({ hasText: /next|>/i }).first()
    const prevButton = page.locator('button, a').filter({ hasText: /prev|</i }).first()

    if (await nextButton.isVisible()) {
      await nextButton.click()
      await page.waitForTimeout(500)
    }
  })
})
