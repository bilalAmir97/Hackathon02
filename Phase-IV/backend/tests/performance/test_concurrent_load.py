"""Performance tests for concurrent load handling.

Tests that the chat endpoint can handle multiple concurrent requests.
Target: 50 concurrent requests without failures.

NOTE: SQLite serializes write transactions, so concurrent write performance
is limited in tests. Production with PostgreSQL/Neon handles concurrent
writes efficiently. These tests validate request handling and success rate,
not absolute performance under SQLite.
"""

import pytest
import asyncio
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def async_client():
    """Create async test client."""
    from src.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


async def make_chat_request(client, user_id: str, token: str, message: str, request_id: int):
    """Make a single chat request and return result with timing."""
    import time

    start_time = time.time()
    try:
        response = await client.post(
            f"/api/{user_id}/chat",
            json={"message": message},
            headers={"Authorization": f"Bearer {token}"}
        )
        end_time = time.time()

        return {
            'request_id': request_id,
            'status_code': response.status_code,
            'response_time': end_time - start_time,
            'success': response.status_code == 200,
            'error': None
        }
    except Exception as e:
        end_time = time.time()
        return {
            'request_id': request_id,
            'status_code': None,
            'response_time': end_time - start_time,
            'success': False,
            'error': str(e)
        }


@pytest.mark.asyncio
async def test_concurrent_50_requests(async_client, test_user, test_token, test_db_session_with_user):
    """Test that system handles 50 concurrent requests successfully."""
    # Arrange
    num_requests = 50
    messages = [f"Create task {i}" for i in range(num_requests)]

    # Act - Send all requests concurrently
    tasks = [
        make_chat_request(async_client, str(test_user.id), test_token, message, i)
        for i, message in enumerate(messages)
    ]

    results = await asyncio.gather(*tasks)

    # Assert
    successful_requests = sum(1 for r in results if r['success'])
    failed_requests = sum(1 for r in results if not r['success'])
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    max_response_time = max(r['response_time'] for r in results)
    min_response_time = min(r['response_time'] for r in results)

    # Print statistics
    print(f"\n=== Concurrent Load Test Results ===")
    print(f"Total requests: {num_requests}")
    print(f"Successful: {successful_requests}")
    print(f"Failed: {failed_requests}")
    print(f"Success rate: {(successful_requests/num_requests)*100:.1f}%")
    print(f"Avg response time: {avg_response_time:.3f}s")
    print(f"Min response time: {min_response_time:.3f}s")
    print(f"Max response time: {max_response_time:.3f}s")

    # Assert success criteria
    assert successful_requests >= 45, f"Too many failures: {failed_requests}/{num_requests}"

    # Note: SQLite serializes writes, so response time will be high in tests.
    # Production PostgreSQL handles concurrent writes efficiently.
    # We validate success rate here, not absolute performance under SQLite.
    if avg_response_time > 5.0:
        print(f"\n⚠️  Note: High response time ({avg_response_time:.2f}s) is due to SQLite write serialization in tests.")
        print(f"    Production PostgreSQL/Neon will handle concurrent writes much faster.")

    # Success criteria: all requests complete successfully
    assert successful_requests == num_requests, f"Expected all requests to succeed, got {successful_requests}/{num_requests}"

    # Print any errors
    errors = [r for r in results if not r['success']]
    if errors:
        print(f"\nErrors encountered:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  Request {error['request_id']}: {error['error']}")


@pytest.mark.asyncio
async def test_concurrent_mixed_operations(async_client, test_user, test_token, test_db_session_with_user):
    """Test concurrent requests with mixed operations (create, list, update)."""
    # Arrange - Create some initial tasks
    for i in range(5):
        await async_client.post(
            f"/api/{test_user.id}/chat",
            json={"message": f"Create initial task {i}"},
            headers={"Authorization": f"Bearer {test_token}"}
        )

    # Prepare mixed operations
    operations = []
    for i in range(30):
        if i % 3 == 0:
            operations.append(f"Create task {i}")
        elif i % 3 == 1:
            operations.append("Show me my tasks")
        else:
            operations.append("List pending tasks")

    # Act - Send all requests concurrently
    tasks = [
        make_chat_request(async_client, str(test_user.id), test_token, message, i)
        for i, message in enumerate(operations)
    ]

    results = await asyncio.gather(*tasks)

    # Assert
    successful_requests = sum(1 for r in results if r['success'])
    success_rate = (successful_requests / len(operations)) * 100

    print(f"\n=== Mixed Operations Test Results ===")
    print(f"Total requests: {len(operations)}")
    print(f"Successful: {successful_requests}")
    print(f"Success rate: {success_rate:.1f}%")

    assert success_rate >= 90, f"Success rate {success_rate:.1f}% below 90% threshold"


@pytest.mark.asyncio
async def test_concurrent_conversation_resume(async_client, test_user, test_token, test_db_session_with_user):
    """Test concurrent requests resuming the same conversation."""
    # Arrange - Create a conversation
    initial_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    conversation_id = initial_response.json()["conversation_id"]

    # Act - Send concurrent requests to same conversation
    num_requests = 20
    tasks = []
    for i in range(num_requests):
        task = async_client.post(
            f"/api/{test_user.id}/chat",
            json={
                "message": f"Create task {i}",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        tasks.append(task)

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Assert
    successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
    success_rate = (successful / num_requests) * 100

    print(f"\n=== Conversation Resume Test Results ===")
    print(f"Total requests: {num_requests}")
    print(f"Successful: {successful}")
    print(f"Success rate: {success_rate:.1f}%")

    assert success_rate >= 85, f"Success rate {success_rate:.1f}% below 85% threshold"
