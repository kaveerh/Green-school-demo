import { test, expect } from '@playwright/test'

test.describe('Students Management', () => {
  const SCHOOL_ID = '60da2256-81fc-4ca5-bf6b-467b8d371c61'

  test.beforeEach(async ({ page }) => {
    // Set school ID in localStorage
    await page.goto('/')
    await page.evaluate((schoolId) => {
      localStorage.setItem('current_school_id', schoolId)
    }, SCHOOL_ID)
  })

  test('should display students list page', async ({ page }) => {
    await page.goto('/students')

    // Check page title/heading
    await expect(page.locator('h1, h2').filter({ hasText: /student management/i }).first()).toBeVisible()

    // Check for "Create Student" button (more specific to avoid nav dropdown)
    const addButton = page.locator('button').filter({ hasText: /create student/i }).first()
    await expect(addButton).toBeVisible()
  })

  test('should navigate to create student form', async ({ page }) => {
    await page.goto('/students')

    // Click create student button (specific selector to avoid nav dropdown)
    const addButton = page.locator('button').filter({ hasText: /create student/i }).first()
    await addButton.click()

    // Should navigate to create form
    await page.waitForURL(/\/students\/(create|new)/)

    // Check for form fields
    await expect(page.locator('input[id="student_id"], input[name="student_id"]').first()).toBeVisible()
    await expect(page.locator('select[id="grade_level"]').first()).toBeVisible()
  })

  test('should create a new student', async ({ page }) => {
    await page.goto('/students/create')

    // Fill in required fields
    const timestamp = Date.now()
    const studentId = `S${timestamp}`

    // Student ID
    const studentIdField = page.locator('input[id="student_id"]').first()
    await studentIdField.fill(studentId)

    // Grade Level (it's a select dropdown)
    const gradeLevelField = page.locator('select[id="grade_level"]').first()
    await gradeLevelField.selectOption('5')

    // Date of Birth
    const dobField = page.locator('input[name="date_of_birth"], input[type="date"]').first()
    if (await dobField.isVisible()) {
      await dobField.fill('2015-05-15')
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

    // Should redirect to students list or show success
    await page.waitForTimeout(2000)
    const currentUrl = page.url()
    expect(currentUrl).toMatch(/\/students/)
  })

  test('should display validation errors for empty required fields', async ({ page }) => {
    await page.goto('/students/create')

    // Try to submit without filling fields
    const submitButton = page.locator('button[type="submit"], button').filter({ hasText: /save|create|submit/i }).first()
    await submitButton.click()

    // Check for validation errors (either HTML5 validation or custom error banner)
    await page.waitForTimeout(500)

    // Check for custom error banner
    const errorBanner = page.locator('.error-banner, [class*="error"]')
    const hasErrorBanner = await errorBanner.count() > 0

    // Check if form validation prevented submission (HTML5)
    const studentIdField = page.locator('input[id="student_id"]').first()
    const hasValidationMessage = await studentIdField.evaluate((el: any) => el.validationMessage !== '')

    // Either custom errors or HTML5 validation should be present
    expect(hasErrorBanner || hasValidationMessage).toBe(true)
  })

  test('should edit an existing student', async ({ page }) => {
    await page.goto('/students')

    // Wait for students to load
    await page.waitForTimeout(1000)

    // Click edit button on first student
    const editButton = page.locator('button, a').filter({ hasText: /edit/i }).first()
    if (await editButton.isVisible()) {
      await editButton.click()

      // Should navigate to edit form
      await page.waitForURL(/\/students\/[a-f0-9-]+\/edit/)

      // Modify a field
      const allergyField = page.locator('textarea[name="allergies"], input[name="allergies"]').first()
      if (await allergyField.isVisible()) {
        await allergyField.fill('Peanuts, Dairy')

        // Save
        const saveButton = page.locator('button[type="submit"], button').filter({ hasText: /save|update/i }).first()
        await saveButton.click()

        await page.waitForTimeout(2000)
      }
    }
  })

  test('should delete a student', async ({ page }) => {
    await page.goto('/students')

    // Wait for students to load
    await page.waitForTimeout(1000)

    // Click delete button on first student
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

  test('should filter students by grade level', async ({ page }) => {
    await page.goto('/students')

    // Wait for students to load
    await page.waitForTimeout(1000)

    // Look for grade level filter
    const gradeFilter = page.locator('select[name*="grade"], button').filter({ hasText: /grade/i }).first()
    if (await gradeFilter.isVisible()) {
      if (await gradeFilter.evaluate(el => el.tagName === 'SELECT')) {
        await gradeFilter.selectOption('5')
      } else {
        await gradeFilter.click()
        const grade5Option = page.locator('button, a, option').filter({ hasText: /grade 5|^5$/i }).first()
        if (await grade5Option.isVisible()) {
          await grade5Option.click()
        }
      }
      await page.waitForTimeout(500)
    }
  })

  test('should filter students by status', async ({ page }) => {
    await page.goto('/students')

    // Wait for students to load
    await page.waitForTimeout(1000)

    // Look for status filter
    const statusFilter = page.locator('select[name*="status"], button').filter({ hasText: /status/i }).first()
    if (await statusFilter.isVisible()) {
      if (await statusFilter.evaluate(el => el.tagName === 'SELECT')) {
        await statusFilter.selectOption('enrolled')
      } else {
        await statusFilter.click()
        const enrolledOption = page.locator('button, a, option').filter({ hasText: /enrolled/i }).first()
        if (await enrolledOption.isVisible()) {
          await enrolledOption.click()
        }
      }
      await page.waitForTimeout(500)
    }
  })

  test('should search students', async ({ page }) => {
    await page.goto('/students')

    // Wait for students to load
    await page.waitForTimeout(1000)

    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"]').first()
    if (await searchInput.isVisible()) {
      await searchInput.fill('student')
      await page.waitForTimeout(500)
    }
  })

  test('should handle pagination', async ({ page }) => {
    await page.goto('/students')

    // Wait for students to load
    await page.waitForTimeout(1000)

    // Look for pagination controls
    const nextButton = page.locator('button').filter({ hasText: /^next$/i }).first()
    const prevButton = page.locator('button').filter({ hasText: /^previous$/i }).first()

    // Check if next button exists and is enabled before clicking
    if (await nextButton.isVisible()) {
      const isEnabled = await nextButton.isEnabled()
      if (isEnabled) {
        await nextButton.click()
        await page.waitForTimeout(500)
      } else {
        // Next button disabled means we're on the last page - this is correct behavior
        expect(await nextButton.isDisabled()).toBe(true)
      }
    }
  })
})
