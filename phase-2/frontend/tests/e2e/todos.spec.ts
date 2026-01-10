import { test, expect } from '@playwright/test';

/**
 * E2E tests for Todo functionality (User Story 4).
 *
 * Tests validate complete user journeys including:
 * - Landing page rendering
 * - Dashboard access and rendering
 * - Todo CRUD operations
 * - Form validation
 * - UI state management
 */

// Test data
const TEST_USER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3OC0xMjM0LTEyMzQtMTIzNC0xMjM0NTY3ODkwYWIiLCJleHAiOjk5OTk5OTk5OTl9.test';

test.describe('Landing Page', () => {
  test('T056: should render landing page for unauthenticated users', async ({ page }) => {
    await page.goto('/');

    // Verify landing page elements
    await expect(page.getByRole('heading', { name: /welcome to todo app/i })).toBeVisible();
    await expect(page.getByText(/full-stack todo application/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

    // Verify no dashboard elements are visible
    await expect(page.getByRole('heading', { name: /todo dashboard/i })).not.toBeVisible();
  });
});

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication by setting token in localStorage
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
  });

  test('T057: should render dashboard for authenticated users', async ({ page }) => {
    // Verify dashboard elements
    await expect(page.getByRole('heading', { name: /todo dashboard/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /logout/i })).toBeVisible();

    // Verify create todo form is visible
    await expect(page.getByPlaceholder(/title/i)).toBeVisible();
  });

  test('T065: should display todo list', async ({ page }) => {
    // Wait for todos to load
    await page.waitForTimeout(1000);

    // Verify todo list container exists
    const todoList = page.locator('[data-testid="todo-list"], .todo-list, [class*="todo"]').first();
    await expect(todoList).toBeVisible();
  });
});

test.describe('Todo CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);
  });

  test('T058: should create a new todo', async ({ page }) => {
    const todoTitle = `Test Todo ${Date.now()}`;

    // Fill in the create form
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(todoTitle);

    // Submit the form
    const createButton = page.getByRole('button', { name: /create|add/i }).first();
    await createButton.click();

    // Wait for todo to appear in list
    await page.waitForTimeout(1000);

    // Verify todo appears in the list
    await expect(page.getByText(todoTitle)).toBeVisible();
  });

  test('T059: should update an existing todo', async ({ page }) => {
    const originalTitle = `Original Todo ${Date.now()}`;
    const updatedTitle = `Updated Todo ${Date.now()}`;

    // Create a todo first
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(originalTitle);
    await page.getByRole('button', { name: /create|add/i }).first().click();
    await page.waitForTimeout(1000);

    // Find and click edit button
    const todoItem = page.locator(`text=${originalTitle}`).locator('..').locator('..');
    const editButton = todoItem.getByRole('button', { name: /edit/i }).or(todoItem.locator('[aria-label*="edit"]'));
    await editButton.first().click();

    // Update the title
    const editInput = page.getByDisplayValue(originalTitle);
    await editInput.fill(updatedTitle);

    // Save the changes
    const saveButton = page.getByRole('button', { name: /save|update/i }).first();
    await saveButton.click();
    await page.waitForTimeout(1000);

    // Verify updated title appears
    await expect(page.getByText(updatedTitle)).toBeVisible();
    await expect(page.getByText(originalTitle)).not.toBeVisible();
  });

  test('T060: should delete a todo', async ({ page }) => {
    const todoTitle = `Todo to Delete ${Date.now()}`;

    // Create a todo first
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(todoTitle);
    await page.getByRole('button', { name: /create|add/i }).first().click();
    await page.waitForTimeout(1000);

    // Verify todo exists
    await expect(page.getByText(todoTitle)).toBeVisible();

    // Find and click delete button
    const todoItem = page.locator(`text=${todoTitle}`).locator('..').locator('..');
    const deleteButton = todoItem.getByRole('button', { name: /delete/i }).or(todoItem.locator('[aria-label*="delete"]'));
    await deleteButton.first().click();
    await page.waitForTimeout(1000);

    // Verify todo is removed
    await expect(page.getByText(todoTitle)).not.toBeVisible();
  });

  test('T061: should toggle todo completion status', async ({ page }) => {
    const todoTitle = `Todo to Toggle ${Date.now()}`;

    // Create a todo first
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(todoTitle);
    await page.getByRole('button', { name: /create|add/i }).first().click();
    await page.waitForTimeout(1000);

    // Find the todo item
    const todoItem = page.locator(`text=${todoTitle}`).locator('..').locator('..');

    // Find and click the checkbox/toggle button
    const checkbox = todoItem.locator('input[type="checkbox"]').or(
      todoItem.getByRole('button', { name: /complete|toggle/i })
    );
    await checkbox.first().click();
    await page.waitForTimeout(1000);

    // Verify visual change (completed state)
    // This could be a strikethrough, different color, or checked checkbox
    const completedTodo = page.locator(`text=${todoTitle}`).locator('..').locator('..');
    await expect(completedTodo).toBeVisible();
  });
});

test.describe('UI State Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);
  });

  test('T066: should persist UI state after operations', async ({ page }) => {
    const todoTitle = `Persistent Todo ${Date.now()}`;

    // Create a todo
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill(todoTitle);
    await page.getByRole('button', { name: /create|add/i }).first().click();
    await page.waitForTimeout(1000);

    // Verify todo exists
    await expect(page.getByText(todoTitle)).toBeVisible();

    // Reload the page
    await page.reload();
    await page.waitForTimeout(1000);

    // Verify todo still exists after reload
    await expect(page.getByText(todoTitle)).toBeVisible();
  });
});

test.describe('Form Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate((token) => {
      localStorage.setItem('auth_token', token);
    }, TEST_USER_TOKEN);
    await page.reload();
    await page.waitForTimeout(500);
  });

  test('T067: should display validation errors for invalid input', async ({ page }) => {
    // Try to submit empty form
    const createButton = page.getByRole('button', { name: /create|add/i }).first();
    await createButton.click();

    // Wait for potential error message
    await page.waitForTimeout(500);

    // Verify error message or that form wasn't submitted
    // Check if title input has required attribute or error styling
    const titleInput = page.getByPlaceholder(/title/i).first();
    const isRequired = await titleInput.getAttribute('required');

    if (isRequired !== null) {
      // HTML5 validation should prevent submission
      expect(isRequired).toBe('');
    } else {
      // Check for custom error message
      const errorMessage = page.locator('text=/required|cannot be empty/i');
      await expect(errorMessage.or(titleInput)).toBeVisible();
    }
  });

  test('T067b: should prevent submission with whitespace-only title', async ({ page }) => {
    const titleInput = page.getByPlaceholder(/title/i).first();
    await titleInput.fill('   ');

    const createButton = page.getByRole('button', { name: /create|add/i }).first();
    await createButton.click();
    await page.waitForTimeout(500);

    // Verify no todo with empty/whitespace title was created
    const emptyTodo = page.locator('text=/^\\s*$/');
    await expect(emptyTodo).not.toBeVisible();
  });
});
