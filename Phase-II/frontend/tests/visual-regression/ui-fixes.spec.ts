import { test, expect } from '@playwright/test';

test.describe('UI Fixes - Visual Regression Tests', () => {
  test('should render landing page correctly at desktop viewport', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveScreenshot('landing-desktop.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01 // Allow for minor pixel differences
    });
  });

  test('should render landing page correctly at tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 800, height: 1024 });
    await page.goto('/');
    await expect(page).toHaveScreenshot('landing-tablet.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });

  test('should render landing page correctly at mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await expect(page).toHaveScreenshot('landing-mobile.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });

  test('should render login page correctly at desktop viewport', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveScreenshot('login-desktop.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });

  test('should render login page correctly at mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/login');
    await expect(page).toHaveScreenshot('login-mobile.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });

  test('should render register page correctly at desktop viewport', async ({ page }) => {
    await page.goto('/register');
    await expect(page).toHaveScreenshot('register-desktop.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });

  test('should render register page correctly at mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/register');
    await expect(page).toHaveScreenshot('register-mobile.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });

  test('should respect reduced motion preferences', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/');

    // Verify that animations are disabled or minimized
    const scanLine = await page.$('.scan-line');
    expect(scanLine).toBeFalsy(); // Scan line should be hidden when reduced motion is enabled

    await expect(page).toHaveScreenshot('landing-reduced-motion.png', {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });
});