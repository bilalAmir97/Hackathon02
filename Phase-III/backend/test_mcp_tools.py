#!/usr/bin/env python3
"""Simple test script to verify MCP server functionality.

This script demonstrates how to interact with the MCP Todo server
by invoking each of the 5 tools in sequence.
"""

import asyncio
import json
from uuid import uuid4

# Mock headers for testing (in production, these would come from MCP context)
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_EMAIL = "test@example.com"

# Import tools
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
from src.mcp.tools.complete_task import complete_task
from src.mcp.tools.update_task import update_task
from src.mcp.tools.delete_task import delete_task
from src.auth.token import create_access_token


async def test_mcp_tools():
    """Test all MCP tools in sequence."""

    # Generate test JWT token
    token = create_access_token(user_id=TEST_USER_ID, email=TEST_EMAIL)
    headers = {"authorization": f"Bearer {token}"}

    print("=" * 60)
    print("MCP Todo Server - Tool Test Suite")
    print("=" * 60)

    # Test 1: add_task
    print("\n1. Testing add_task...")
    try:
        task1 = await add_task(
            {"title": "Buy groceries", "description": "Milk, eggs, bread"},
            headers
        )
        print(f"✓ Created task: {task1['id']}")
        print(f"  Title: {task1['title']}")
        print(f"  Status: {task1['status']}")
        print(f"  Version: {task1['version']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 2: add_task (second task)
    print("\n2. Testing add_task (second task)...")
    try:
        task2 = await add_task(
            {"title": "Write report", "description": None},
            headers
        )
        print(f"✓ Created task: {task2['id']}")
        print(f"  Title: {task2['title']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 3: list_tasks
    print("\n3. Testing list_tasks (all)...")
    try:
        tasks = await list_tasks({"status": "all"}, headers)
        print(f"✓ Retrieved {tasks['count']} tasks")
        for task in tasks['tasks']:
            print(f"  - {task['title']} ({task['status']})")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 4: update_task
    print("\n4. Testing update_task...")
    try:
        updated = await update_task(
            {
                "task_id": task1['id'],
                "title": "Buy groceries and snacks",
                "description": "Milk, eggs, bread, chips"
            },
            headers
        )
        print(f"✓ Updated task: {updated['id']}")
        print(f"  New title: {updated['title']}")
        print(f"  New version: {updated['version']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 5: complete_task
    print("\n5. Testing complete_task...")
    try:
        completed = await complete_task(
            {"task_id": task1['id']},
            headers
        )
        print(f"✓ Completed task: {completed['id']}")
        print(f"  Status: {completed['status']}")
        print(f"  Version: {completed['version']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 6: list_tasks (pending only)
    print("\n6. Testing list_tasks (pending only)...")
    try:
        pending = await list_tasks({"status": "pending"}, headers)
        print(f"✓ Retrieved {pending['count']} pending tasks")
        for task in pending['tasks']:
            print(f"  - {task['title']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 7: delete_task
    print("\n7. Testing delete_task...")
    try:
        deleted = await delete_task(
            {"task_id": task2['id']},
            headers
        )
        print(f"✓ Deleted task: {deleted['task_id']}")
        print(f"  Success: {deleted['success']}")
        print(f"  Message: {deleted['message']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Test 8: list_tasks (final state)
    print("\n8. Testing list_tasks (final state)...")
    try:
        final = await list_tasks({"status": "all"}, headers)
        print(f"✓ Retrieved {final['count']} tasks")
        for task in final['tasks']:
            print(f"  - {task['title']} ({task['status']})")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
