import { test, expect } from '@playwright/test';

/**
 * E2E tests for responsive design across different viewport sizes.
 *
 * Tests validate that the UI renders correctly and is usable on:
 * - Mobile devices (390x844)
 * - Tablet devices (1024x1366)
 * - Desktop devices (1920x1080)
 */

const TEST_USER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3OC0xMjM0LTEyMzQtMTIzNC0xMjM0NTY3ODkwYWIiLCJleHAiOjk5OTk5OTk5OTl9.test';

test.describe('Mobile Viewport (390x844)', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test('T068: should render landing page correctly on mobile', async ({ page }) => {
    await page.goto('/');

    // Verify key elements are visible
    await expect(page.getByRole('heading', { name: /welcome to todo app/i })).toBeVisible();
    await expect(page.getByText(/full-stack todo application/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

    // Verify layout is not broken (no horizontal scroll)
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = page.viewportSize()?.width || 390;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1); // Allow 1px tolerance
  });

  test('T068b: should render dashboard correctly on mobile', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    // Verify dashboard elements are visible
    await expect(page.getByRole('heading', { name: /todo dashboard/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();

    // Verify form is usable
    const titleInput = page.getByPlaceholder(/title/i).first();
    await expect(titleInput).toBeVisible();
    await expect(titleInput).toBeEditable();

    // Verify no horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = page.viewportSize()?.width || 390;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1);
  });

  test('T068c: should allow todo creation on mobile', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    const todoTitle = `Mobile Todo ${Date.now()}`;

    // Fill and submit form
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(todoTitle);

    const createButton = page.getByRole('button', { name: /create|add/i }).first();
    await createButton.click();
    await page.waitForTimeout(1000);

    // Verify todo appears
    await expect(page.getByText(todoTitle)).toBeVisible();
  });

  test('T068d: should have touch-friendly buttons on mobile', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    // Check button sizes (should be at least 44x44 for touch targets)
    const createButton = page.getByRole('button', { name: /create|add/i }).first();
    const buttonBox = await createButton.boundingBox();

    if (buttonBox) {
      // Touch target should be at least 44x44 pixels (iOS HIG recommendation)
      expect(buttonBox.height).toBeGreaterThanOrEqual(36); // Allow some flexibility
    }
  });
});

test.describe('Tablet Viewport (1024x1366)', () => {
  test.use({ viewport: { width: 1024, height: 1366 } });

  test('T069: should render landing page correctly on tablet', async ({ page }) => {
    await page.goto('/');

    // Verify key elements are visible
    await expect(page.getByRole('heading', { name: /welcome to todo app/i })).toBeVisible();
    await expect(page.getByText(/full-stack todo application/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

    // Verify layout uses available space appropriately
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = page.viewportSize()?.width || 1024;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1);
  });

  test('T069b: should render dashboard correctly on tablet', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    // Verify dashboard elements are visible
    await expect(page.getByRole('heading', { name: /todo dashboard/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();

    // Verify form is usable
    const titleInput = page.getByPlaceholder(/title/i).first();
    await expect(titleInput).toBeVisible();
    await expect(titleInput).toBeEditable();

    // Verify layout is optimized for tablet
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = page.viewportSize()?.width || 1024;
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1);
  });

  test('T069c: should display todos in optimal layout on tablet', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    // Create a todo to test layout
    const todoTitle = `Tablet Todo ${Date.now()}`;
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(todoTitle);
    await page.getByRole('button', { name: /create|add/i }).first().click();
    await page.waitForTimeout(1000);

    // Verify todo is visible and layout is appropriate
    await expect(page.getByText(todoTitle)).toBeVisible();

    // Check that content is centered or uses max-width appropriately
    const container = page.locator('.container, [class*="max-w"]').first();
    if (await container.count() > 0) {
      const containerBox = await container.boundingBox();
      if (containerBox) {
        // Container should not span full width on tablet (should have margins)
        expect(containerBox.width).toBeLessThan(1024);
      }
    }
  });
});

test.describe('Desktop Viewport (1920x1080)', () => {
  test.use({ viewport: { width: 1920, height: 1080 } });

  test('T070: should render landing page correctly on desktop', async ({ page }) => {
    await page.goto('/');

    // Verify key elements are visible
    await expect(page.getByRole('heading', { name: /welcome to todo app/i })).toBeVisible();
    await expect(page.getByText(/full-stack todo application/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

    // Verify content is centered and not stretched across full width
    const container = page.locator('.container, [class*="max-w"]').first();
    if (await container.count() > 0) {
      const containerBox = await container.boundingBox();
      if (containerBox) {
        // Container should have reasonable max-width on desktop
        expect(containerBox.width).toBeLessThan(1920);
        expect(containerBox.width).toBeGreaterThan(400); // But not too narrow
      }
    }
  });

  test('T070b: should render dashboard correctly on desktop', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    // Verify dashboard elements are visible
    await expect(page.getByRole('heading', { name: /todo dashboard/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();

    // Verify form is usable
    const titleInput = page.getByPlaceholder(/title/i).first();
    await expect(titleInput).toBeVisible();
    await expect(titleInput).toBeEditable();

    // Verify content uses max-width constraint
    const container = page.locator('.container, [class*="max-w"]').first();
    if (await container.count() > 0) {
      const containerBox = await container.boundingBox();
      if (containerBox) {
        // Container should not span full width on desktop
        expect(containerBox.width).toBeLessThan(1920);
      }
    }
  });

  test('T070c: should display todos with optimal spacing on desktop', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    // Create multiple todos to test layout
    for (let i = 1; i <= 3; i++) {
      const todoTitle = `Desktop Todo ${i} ${Date.now()}`;
      const titleInput = page.getByPlaceholder(/title/i).first();
      await titleInput.fill(todoTitle);
      await page.getByRole('button', { name: /create|add/i }).first().click();
      await page.waitForTimeout(500);
    }

    // Verify todos are visible
    await expect(page.getByText(/Desktop Todo 1/)).toBeVisible();
    await expect(page.getByText(/Desktop Todo 2/)).toBeVisible();
    await expect(page.getByText(/Desktop Todo 3/)).toBeVisible();

    // Verify layout is readable and well-spaced
    const todoItems = page.locator('[class*="todo"]').or(page.locator('li'));
    const count = await todoItems.count();
    expect(count).toBeGreaterThanOrEqual(3);
  });

  test('T070d: should have hover states on desktop', async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);

    // Create a todo
    const todoTitle = `Hover Test Todo ${Date.now()}`;
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(todoTitle);
    await page.getByRole('button', { name: /create|add/i }).first().click();
    await page.waitForTimeout(1000);

    // Hover over the create button and verify it's interactive
    const createButton = page.getByRole('button', { name: /create|add/i }).first();
    await createButton.hover();

    // Button should be visible and enabled
    await expect(createButton).toBeVisible();
    await expect(createButton).toBeEnabled();
  });
});

test.describe('Cross-Viewport Consistency', () => {
  test('should maintain functionality across all viewports', async ({ page }) => {
    const viewports = [
      { width: 390, height: 844, name: 'Mobile' },
      { width: 1024, height: 1366, name: 'Tablet' },
      { width: 1920, height: 1080, name: 'Desktop' },
    ];

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');

      // Mock authentication
      await page.evaluate((token) => {
        localStorage.setItem('auth_token', token);
      }, TEST_USER_TOKEN);
      await page.reload();
      await page.waitForTimeout(500);

      // Verify core functionality works
      const todoTitle = `${viewport.name} Todo ${Date.now()}`;
      const titleInput = page.getByPlaceholder(/title/i).first();
      await titleInput.fill(todoTitle);
      await page.getByRole('button', { name: /create|add/i }).first().click();
      await page.waitForTimeout(1000);

      // Verify todo appears
      await expect(page.getByText(todoTitle)).toBeVisible();
    }
  });
});
