#!/usr/bin/env python3
"""
Unit tests for Evolution of Todo - Phase I
"""

import unittest
import sys
import os

# Add parent directory to path to import todo_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from todo_app.todo_app import Task, TaskManager, CLIInterface, TodoApp, MAX_DESCRIPTION_LENGTH


class TestTask(unittest.TestCase):
    """Tests for Task class"""

    def test_task_creation(self):
        """Test basic task creation"""
        task = Task(0, "Test task", False)
        self.assertEqual(task.id, 0)
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.completed, False)

    def test_task_creation_with_completed(self):
        """Test task creation with completed status"""
        task = Task(1, "Completed task", True)
        self.assertEqual(task.id, 1)
        self.assertEqual(task.description, "Completed task")
        self.assertEqual(task.completed, True)

    def test_task_str_incomplete(self):
        """Test string representation of incomplete task"""
        task = Task(0, "Test task", False)
        result = str(task)
        self.assertIn("ID 0", result)
        self.assertIn("Test task", result)
        self.assertIn("[ ]", result)

    def test_task_str_complete(self):
        """Test string representation of complete task"""
        task = Task(1, "Completed task", True)
        result = str(task)
        self.assertIn("ID 1", result)
        self.assertIn("Completed task", result)
        self.assertIn("[X]", result)


class TestTaskManager(unittest.TestCase):
    """Tests for TaskManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = TaskManager()

    def test_initialization(self):
        """Test TaskManager initialization"""
        self.assertEqual(len(self.manager.tasks), 0)
        self.assertEqual(self.manager.next_id, 0)

    def test_add_task_success(self):
        """Test adding a valid task"""
        task = self.manager.add_task("Test task")
        self.assertIsNotNone(task)
        self.assertEqual(task.id, 0)
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.completed, False)

    def test_add_task_sequential_ids(self):
        """Test that task IDs are assigned sequentially starting from 0"""
        task1 = self.manager.add_task("Task 1")
        task2 = self.manager.add_task("Task 2")
        task3 = self.manager.add_task("Task 3")

        self.assertEqual(task1.id, 0)
        self.assertEqual(task2.id, 1)
        self.assertEqual(task3.id, 2)

    def test_add_task_empty_description(self):
        """Test adding task with empty description"""
        task = self.manager.add_task("")
        self.assertIsNone(task)

    def test_add_task_whitespace_description(self):
        """Test adding task with whitespace-only description"""
        task = self.manager.add_task("   ")
        self.assertIsNone(task)

    def test_add_task_max_length(self):
        """Test adding task at maximum description length"""
        description = "x" * MAX_DESCRIPTION_LENGTH
        task = self.manager.add_task(description)
        self.assertIsNotNone(task)
        self.assertEqual(task.description, description)

    def test_add_task_exceeds_max_length(self):
        """Test adding task exceeding maximum description length"""
        description = "x" * (MAX_DESCRIPTION_LENGTH + 1)
        task = self.manager.add_task(description)
        self.assertIsNone(task)

    def test_add_task_strips_whitespace(self):
        """Test that task descriptions are trimmed"""
        task = self.manager.add_task("  Test task  ")
        self.assertIsNotNone(task)
        self.assertEqual(task.description, "Test task")

    def test_get_task_exists(self):
        """Test getting an existing task"""
        self.manager.add_task("Test task")
        task = self.manager.get_task(0)
        self.assertIsNotNone(task)
        self.assertEqual(task.description, "Test task")

    def test_get_task_not_exists(self):
        """Test getting a non-existent task"""
        task = self.manager.get_task(999)
        self.assertIsNone(task)

    def test_get_all_tasks_empty(self):
        """Test getting all tasks when list is empty"""
        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 0)

    def test_get_all_tasks_sorted(self):
        """Test that get_all_tasks returns tasks sorted by ID"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.add_task("Task 3")

        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].id, 0)
        self.assertEqual(tasks[1].id, 1)
        self.assertEqual(tasks[2].id, 2)

    def test_update_task_success(self):
        """Test updating task description"""
        self.manager.add_task("Original description")
        success = self.manager.update_task(0, "Updated description")

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertEqual(task.description, "Updated description")

    def test_update_task_not_exists(self):
        """Test updating non-existent task"""
        success = self.manager.update_task(999, "New description")
        self.assertFalse(success)

    def test_update_task_empty_description(self):
        """Test updating task with empty description"""
        self.manager.add_task("Original description")
        success = self.manager.update_task(0, "")
        self.assertFalse(success)

    def test_update_task_exceeds_max_length(self):
        """Test updating task with description exceeding max length"""
        self.manager.add_task("Original description")
        description = "x" * (MAX_DESCRIPTION_LENGTH + 1)
        success = self.manager.update_task(0, description)
        self.assertFalse(success)

    def test_mark_complete_success(self):
        """Test marking task as complete"""
        self.manager.add_task("Test task")
        success = self.manager.mark_complete(0)

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertTrue(task.completed)

    def test_mark_complete_not_exists(self):
        """Test marking non-existent task as complete"""
        success = self.manager.mark_complete(999)
        self.assertFalse(success)

    def test_mark_incomplete_success(self):
        """Test marking task as incomplete"""
        task = self.manager.add_task("Test task")
        task.completed = True

        success = self.manager.mark_incomplete(0)

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertFalse(task.completed)

    def test_mark_incomplete_not_exists(self):
        """Test marking non-existent task as incomplete"""
        success = self.manager.mark_incomplete(999)
        self.assertFalse(success)

    def test_delete_task_success(self):
        """Test deleting an existing task"""
        self.manager.add_task("Test task")
        success = self.manager.delete_task(0)

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertIsNone(task)

    def test_delete_task_not_exists(self):
        """Test deleting non-existent task"""
        success = self.manager.delete_task(999)
        self.assertFalse(success)

    def test_delete_task_maintains_id_gaps(self):
        """Test that deleting tasks maintains ID gaps (no ID reuse)"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.add_task("Task 3")

        # Delete task with ID 1
        self.manager.delete_task(1)

        # Add a new task - should get ID 3, not reuse ID 1
        task = self.manager.add_task("Task 4")
        self.assertEqual(task.id, 3)

        # Verify task 1 is still None
        self.assertIsNone(self.manager.get_task(1))


class TestCLIInterface(unittest.TestCase):
    """Tests for CLIInterface class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = TaskManager()
        self.cli = CLIInterface(self.manager)

    def test_initialization(self):
        """Test CLIInterface initialization"""
        self.assertIsNotNone(self.cli.task_manager)
        self.assertEqual(self.cli.task_manager, self.manager)


class TestTodoApp(unittest.TestCase):
    """Tests for TodoApp class"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = TodoApp()

    def test_initialization(self):
        """Test TodoApp initialization"""
        self.assertIsNotNone(self.app.task_manager)
        self.assertIsNotNone(self.app.cli)
        self.assertTrue(self.app.running)


class TestUserStories(unittest.TestCase):
    """Integration tests for user stories"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = TaskManager()

    def test_user_story_1_add_task(self):
        """
        User Story 1: Add New Tasks
        Acceptance Scenario 1: Add task and see it in list
        """
        task = self.manager.add_task("Buy groceries")
        self.assertIsNotNone(task)

        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].description, "Buy groceries")

    def test_user_story_1_first_task_id(self):
        """
        User Story 1: Add New Tasks
        Acceptance Scenario 2: First task gets ID 0
        """
        task = self.manager.add_task("First task")
        self.assertEqual(task.id, 0)

    def test_user_story_1_next_available_id(self):
        """
        User Story 1: Add New Tasks
        Acceptance Scenario 3: New task gets next available ID
        """
        task1 = self.manager.add_task("Task 1")
        task2 = self.manager.add_task("Task 2")

        self.assertEqual(task1.id, 0)
        self.assertEqual(task2.id, 1)

    def test_user_story_2_view_all_tasks(self):
        """
        User Story 2: View Task List
        Acceptance Scenario 1: All tasks displayed with ID, description, status
        """
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.mark_complete(1)

        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].id, 0)
        self.assertEqual(tasks[0].description, "Task 1")
        self.assertFalse(tasks[0].completed)
        self.assertEqual(tasks[1].id, 1)
        self.assertEqual(tasks[1].description, "Task 2")
        self.assertTrue(tasks[1].completed)

    def test_user_story_2_empty_list(self):
        """
        User Story 2: View Task List
        Acceptance Scenario 2: Empty list message
        """
        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 0)

    def test_user_story_3_mark_complete(self):
        """
        User Story 3: Mark Task Complete/Incomplete
        Acceptance Scenario 1: Valid task ID changes to complete
        """
        self.manager.add_task("Test task")
        success = self.manager.mark_complete(0)

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertTrue(task.completed)

    def test_user_story_3_mark_incomplete(self):
        """
        User Story 3: Mark Task Complete/Incomplete
        Acceptance Scenario 2: Completed task changes to incomplete
        """
        task = self.manager.add_task("Test task")
        self.manager.mark_complete(0)
        success = self.manager.mark_incomplete(0)

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertFalse(task.completed)

    def test_user_story_3_invalid_id(self):
        """
        User Story 3: Mark Task Complete/Incomplete
        Acceptance Scenario 3: Invalid ID shows error
        """
        success = self.manager.mark_complete(999)
        self.assertFalse(success)

    def test_user_story_4_update_task(self):
        """
        User Story 4: Update Task Description
        Acceptance Scenario 1: Valid task updated with new description
        """
        self.manager.add_task("Original description")
        success = self.manager.update_task(0, "Updated description")

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertEqual(task.description, "Updated description")

    def test_user_story_4_invalid_id(self):
        """
        User Story 4: Update Task Description
        Acceptance Scenario 2: Invalid ID shows error
        """
        success = self.manager.update_task(999, "New description")
        self.assertFalse(success)

    def test_user_story_4_empty_description(self):
        """
        User Story 4: Update Task Description
        Acceptance Scenario 3: Empty description shows error
        """
        self.manager.add_task("Original description")
        success = self.manager.update_task(0, "")
        self.assertFalse(success)

    def test_user_story_5_delete_task(self):
        """
        User Story 5: Delete Task
        Acceptance Scenario 1: Valid task removed from list
        """
        self.manager.add_task("Test task")
        success = self.manager.delete_task(0)

        self.assertTrue(success)
        task = self.manager.get_task(0)
        self.assertIsNone(task)

    def test_user_story_5_invalid_id(self):
        """
        User Story 5: Delete Task
        Acceptance Scenario 2: Invalid ID shows error
        """
        success = self.manager.delete_task(999)
        self.assertFalse(success)

    def test_user_story_5_id_consistency(self):
        """
        User Story 5: Delete Task
        Acceptance Scenario 3: Deleted task no longer appears, other IDs consistent
        """
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.add_task("Task 3")

        # Delete task 1
        self.manager.delete_task(1)

        # Verify task 1 is gone
        self.assertIsNone(self.manager.get_task(1))

        # Verify other tasks still have their original IDs
        self.assertIsNotNone(self.manager.get_task(0))
        self.assertIsNotNone(self.manager.get_task(2))


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = TaskManager()

    def test_empty_task_list_operations(self):
        """Test operations on empty task list"""
        # View empty list
        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 0)

        # Try to mark non-existent task complete
        success = self.manager.mark_complete(0)
        self.assertFalse(success)

        # Try to delete non-existent task
        success = self.manager.delete_task(0)
        self.assertFalse(success)

    def test_invalid_task_id_operations(self):
        """Test operations with invalid task IDs"""
        self.manager.add_task("Test task")

        # Try invalid ID
        success = self.manager.mark_complete(999)
        self.assertFalse(success)

        success = self.manager.update_task(999, "New description")
        self.assertFalse(success)

        success = self.manager.delete_task(999)
        self.assertFalse(success)

    def test_task_id_after_deletion(self):
        """Test that task IDs remain consistent after deletion"""
        self.manager.add_task("Task 1")
        self.manager.add_task("Task 2")
        self.manager.add_task("Task 3")

        # Delete middle task
        self.manager.delete_task(1)

        # Add new task - should get ID 3, not 1
        new_task = self.manager.add_task("Task 4")
        self.assertEqual(new_task.id, 3)

    def test_very_long_description(self):
        """Test handling of very long descriptions"""
        # At max length - should succeed
        description = "x" * MAX_DESCRIPTION_LENGTH
        task = self.manager.add_task(description)
        self.assertIsNotNone(task)

        # Over max length - should fail
        description = "x" * (MAX_DESCRIPTION_LENGTH + 1)
        task = self.manager.add_task(description)
        self.assertIsNone(task)

    def test_whitespace_descriptions(self):
        """Test handling of empty/whitespace descriptions"""
        # Empty string
        task = self.manager.add_task("")
        self.assertIsNone(task)

        # Whitespace only
        task = self.manager.add_task("   ")
        self.assertIsNone(task)

        # Valid with surrounding whitespace (should be trimmed)
        task = self.manager.add_task("  Valid task  ")
        self.assertIsNotNone(task)
        self.assertEqual(task.description, "Valid task")


if __name__ == "__main__":
    unittest.main()
