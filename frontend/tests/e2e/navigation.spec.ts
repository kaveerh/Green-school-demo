import { test, expect } from '@playwright/test'

test.describe('Navigation Bar', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard to ensure navigation is visible
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
  })

  test('should display all main navigation items', async ({ page }) => {
    // Dashboard
    await expect(page.locator('nav .nav-menu').getByText('Dashboard')).toBeVisible()

    // Management Modules - using role button for dropdowns
    await expect(page.locator('nav').getByRole('button', { name: /users/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /schools/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /teachers/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /students/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /parents/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /subjects/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /rooms/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /classes/i })).toBeVisible()

    // Academic Modules
    await expect(page.locator('nav').getByRole('button', { name: /lessons/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /assessments/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /attendance/i })).toBeVisible()

    // School Operations
    await expect(page.locator('nav').getByRole('button', { name: /events/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /activities/i })).toBeVisible()

    // NEW: Verify Vendors and Merits are present
    await expect(page.locator('nav').getByRole('button', { name: /vendors/i })).toBeVisible()
    await expect(page.locator('nav').getByRole('button', { name: /merits/i })).toBeVisible()
  })

  test('should navigate to Vendors page from dropdown', async ({ page }) => {
    // Click on Vendors dropdown
    await page.locator('nav').getByRole('button', { name: /vendors/i }).click()

    // Wait for a moment for Vue to update
    await page.waitForTimeout(300)

    // Click on "View Vendors" link
    await page.getByText('View Vendors', { exact: true }).click()

    // Should navigate to vendors page
    await page.waitForURL(/\/vendors/, { timeout: 10000 })

    // Verify we're on the vendors page
    await expect(page).toHaveURL(/\/vendors/)
  })

  test('should navigate to Merits page from dropdown', async ({ page }) => {
    // Click on Merits dropdown
    await page.locator('nav').getByRole('button', { name: /merits/i }).click()

    // Wait for a moment for Vue to update
    await page.waitForTimeout(300)

    // Click on "View Merits" link
    await page.getByText('View Merits', { exact: true }).click()

    // Should navigate to merits page
    await page.waitForURL(/\/merits/, { timeout: 10000 })

    // Verify we're on the merits page
    await expect(page).toHaveURL(/\/merits/)
  })

  test('should show Vendors dropdown menu items', async ({ page }) => {
    // Click on Vendors dropdown
    await page.locator('nav').getByRole('button', { name: /vendors/i }).click()

    // Wait for a moment for Vue to update
    await page.waitForTimeout(300)

    // Verify dropdown items are visible
    await expect(page.getByText('View Vendors', { exact: true })).toBeVisible()
    await expect(page.getByText('Create Vendor', { exact: true })).toBeVisible()
  })

  test('should show Merits dropdown menu items', async ({ page }) => {
    // Click on Merits dropdown
    await page.locator('nav').getByRole('button', { name: /merits/i }).click()

    // Wait for a moment for Vue to update
    await page.waitForTimeout(300)

    // Verify dropdown items are visible
    await expect(page.getByText('View Merits', { exact: true })).toBeVisible()
    await expect(page.getByText('Leaderboard', { exact: true })).toBeVisible()
    await expect(page.getByText('Award Merit', { exact: true })).toBeVisible()
  })

  test('should navigate to Merits Leaderboard', async ({ page }) => {
    // Click on Merits dropdown
    await page.locator('nav').getByRole('button', { name: /merits/i }).click()

    // Wait for a moment and click Leaderboard
    await page.waitForTimeout(300)
    await page.getByText('Leaderboard', { exact: true }).click()

    // Should navigate to merits leaderboard
    await page.waitForURL(/\/merits\/leaderboard/, { timeout: 10000 })
    await expect(page).toHaveURL(/\/merits\/leaderboard/)
  })

  test('should highlight active navigation item when on Vendors page', async ({ page }) => {
    // Navigate to vendors page
    await page.goto('/vendors')
    await page.waitForLoadState('networkidle')

    // The Vendors button should have is-active class
    const vendorsButton = page.locator('nav').getByRole('button', { name: /vendors/i })
    await expect(vendorsButton).toHaveClass(/is-active/)
  })

  test('should show all 15 features in navigation', async ({ page }) => {
    // Verify each of the 15 core features is present
    const features = [
      { name: /users/i },
      { name: /schools/i },
      { name: /teachers/i },
      { name: /students/i },
      { name: /parents/i },
      { name: /subjects/i },
      { name: /rooms/i },
      { name: /classes/i },
      { name: /lessons/i },
      { name: /assessments/i },
      { name: /attendance/i },
      { name: /events/i },
      { name: /activities/i },
      { name: /vendors/i },
      { name: /merits/i }
    ]

    // Verify each feature is present as a button
    for (const feature of features) {
      await expect(page.locator('nav').getByRole('button', feature)).toBeVisible()
    }

    // Total should be 15 core features
    expect(features.length).toBe(15)
  })
})
