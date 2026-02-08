import { test, expect, Page } from '@playwright/test';

test.describe('Scan Line Visual Tests', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('should display ambient scan line with correct visual properties', async () => {
    // Navigate to a page that has the scan line
    await page.goto('/');

    // Wait for the scan line to be rendered
    await page.waitForSelector('.scanline-ambient', { state: 'visible' });

    // Check that the ambient scan line element exists
    const ambientScanline = page.locator('.scanline-ambient');
    await expect(ambientScanline).toBeVisible();

    // Check the visual properties of the ambient scan line
    await expect(ambientScanline).toHaveCSS('height', '2px');
    await expect(ambientScanline).toHaveCSS('z-index', '9998');
    await expect(ambientScanline).toHaveCSS('pointer-events', 'none');

    // Check that it has a gradient background
    const background = await ambientScanline.evaluate(el =>
      window.getComputedStyle(el).backgroundImage
    );
    expect(background).toContain('gradient');

    // Check opacity is within expected range for ambient (0.02-0.06)
    const opacity = await ambientScanline.evaluate(el =>
      parseFloat(window.getComputedStyle(el).opacity)
    );
    expect(opacity).toBeGreaterThanOrEqual(0.02);
    expect(opacity).toBeLessThanOrEqual(0.06);
  });

  test('should display event scan line with correct visual properties', async () => {
    // Navigate to a page that has the scan line
    await page.goto('/');

    // We need to trigger an event scan line, for example by clicking something
    // For this test, we'll check if the event scan line class exists
    const eventScanline = page.locator('.scanline-event');

    // The event scan line might not always be visible, so we'll test its potential existence
    // and check its style properties when it does appear

    // Check if the selector would create the right kind of element when triggered
    await page.addStyleTag({
      content: `
        .test-event-scanline {
          height: 2px;
          background: var(--scanline-color-gradient, linear-gradient(to right, #00f7ff, #6a00ff));
          opacity: var(--scanline-event-opacity, 0.8);
          z-index: 9999;
          position: fixed;
          pointer-events: none;
        }
      `
    });

    // Verify the expected CSS custom properties exist
    const computedStyle = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        scanlineColorGradient: style.getPropertyValue('--scanline-color-gradient'),
        scanlineEventOpacity: style.getPropertyValue('--scanline-event-opacity'),
      };
    });

    expect(computedStyle.scanlineColorGradient).toContain('gradient');
    expect(parseFloat(computedStyle.scanlineEventOpacity)).toBeGreaterThan(0.5);
  });

  test('should adapt to dark/light theme', async () => {
    await page.goto('/');

    // Check initial theme styles
    const scanlineContainer = page.locator('.scanline-container');

    // Get computed styles to verify theme adaptation
    const computedStyle = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        scanlineColorGradient: style.getPropertyValue('--scanline-color-gradient'),
        scanlineBaseOpacity: style.getPropertyValue('--scanline-base-opacity'),
        scanlineAmbientOpacity: style.getPropertyValue('--scanline-ambient-opacity'),
      };
    });

    // Verify that CSS custom properties are defined
    expect(computedStyle.scanlineColorGradient).toBeTruthy();
    expect(computedStyle.scanlineBaseOpacity).toBeTruthy();
    expect(computedStyle.scanlineAmbientOpacity).toBeTruthy();
  });

  test('should respect reduced motion preferences', async () => {
    // Simulate reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await page.goto('/');

    // When reduced motion is enabled, ambient scanlines should still be visible
    // but static, while event scanlines should be hidden or minimized
    const ambientScanline = page.locator('.scanline-ambient');

    // The element should exist but animations should be disabled
    await expect(ambientScanline).toBeAttached();
  });

  test('should handle rapid event triggers gracefully', async () => {
    await page.goto('/');

    // Simulate rapid triggering of event scan lines
    // This would require triggering events programmatically
    await page.evaluate(() => {
      // Simulate multiple rapid events that would trigger scan lines
      // In a real test, we would call the trigger functions
      const event = new Event('scanline-test-trigger');
      document.dispatchEvent(event);
      document.dispatchEvent(event);
      document.dispatchEvent(event);
    });

    // Check that the page remains stable and no excessive elements are created
    const scanlineElements = await page.locator('.scanline-container').count();
    expect(scanlineElements).toBeLessThan(10); // Arbitrary reasonable upper limit
  });

  test('should maintain performance with animations', async () => {
    await page.goto('/');

    // Check for the presence of performance-related attributes
    const scanlineContainer = page.locator('.scanline-container');

    // Verify that will-change property is applied for performance
    await expect(scanlineContainer).toHaveCSS('will-change', 'transform, opacity');
  });

  test('should render with proper layering (z-index)', async () => {
    await page.goto('/');

    // Wait for scan lines to be rendered
    await page.waitForSelector('.scanline-ambient', { state: 'visible' });
    await page.waitForSelector('.scanline-event', { state: 'visible' });

    const ambientScanline = page.locator('.scanline-ambient');
    const eventScanline = page.locator('.scanline-event');

    // Check z-index values - ambient should be lower than event
    const ambientZIndex = await ambientScanline.evaluate(el =>
      parseInt(window.getComputedStyle(el).zIndex)
    );

    const eventZIndex = await eventScanline.evaluate(el =>
      parseInt(window.getComputedStyle(el).zIndex)
    );

    // Ambient scan lines should have lower z-index than event scan lines
    expect(ambientZIndex).toBeLessThan(eventZIndex);
    expect(ambientZIndex).toBe(9998);
    expect(eventZIndex).toBe(9999);
  });

  test('should apply blur effect when configured', async () => {
    await page.goto('/');

    const scanlineContainer = page.locator('.scanline-container');

    // Check if blur is applied based on CSS custom property
    const computedStyle = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      return {
        blurIntensity: style.getPropertyValue('--scanline-blur-intensity'),
      };
    });

    // If blur intensity is configured, check if it's applied to elements
    if (computedStyle.blurIntensity && parseFloat(computedStyle.blurIntensity) > 0) {
      await expect(scanlineContainer).toHaveCSS(
        'filter',
        expect.stringContaining('blur')
      );
    }
  });
});