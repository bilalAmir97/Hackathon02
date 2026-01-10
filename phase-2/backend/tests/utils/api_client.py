"""
HTTP client wrapper for API testing.

Provides a convenient interface for making HTTP requests to the FastAPI backend
with automatic header management and response validation.
"""
from typing import Any, Dict, Optional

from fastapi.testclient import TestClient


class APIClient:
    """Wrapper around TestClient for convenient API testing."""

    def __init__(self, client: TestClient):
        """
        Initialize API client.

        Args:
            client: FastAPI TestClient instance
        """
        self.client = client
        self.base_url = "/api"

    def get(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        """
        Make GET request.

        Args:
            path: API endpoint path
            headers: Request headers
            params: Query parameters

        Returns:
            Response object
        """
        url = f"{self.base_url}{path}" if not path.startswith("/api") else path
        return self.client.get(url, headers=headers, params=params)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Make POST request.

        Args:
            path: API endpoint path
            json: Request body as JSON
            headers: Request headers

        Returns:
            Response object
        """
        url = f"{self.base_url}{path}" if not path.startswith("/api") else path
        return self.client.post(url, json=json, headers=headers)

    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Make PUT request.

        Args:
            path: API endpoint path
            json: Request body as JSON
            headers: Request headers

        Returns:
            Response object
        """
        url = f"{self.base_url}{path}" if not path.startswith("/api") else path
        return self.client.put(url, json=json, headers=headers)

    def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Make DELETE request.

        Args:
            path: API endpoint path
            headers: Request headers

        Returns:
            Response object
        """
        url = f"{self.base_url}{path}" if not path.startswith("/api") else path
        return self.client.delete(url, headers=headers)

    def health_check(self):
        """
        Check API health endpoint.

        Returns:
            Response object
        """
        return self.client.get("/health")

    def readiness_check(self):
        """
        Check API readiness endpoint.

        Returns:
            Response object
        """
        return self.client.get("/ready")

    # Todo-specific convenience methods

    def create_todo(self, payload: Dict[str, Any], headers: Dict[str, str]):
        """Create a todo."""
        return self.post("/todos", json=payload, headers=headers)

    def list_todos(self, headers: Dict[str, str]):
        """List all todos for authenticated user."""
        return self.get("/todos", headers=headers)

    def get_todo(self, todo_id: str, headers: Dict[str, str]):
        """Get specific todo by ID."""
        return self.get(f"/todos/{todo_id}", headers=headers)

    def update_todo(self, todo_id: str, payload: Dict[str, Any], headers: Dict[str, str]):
        """Update a todo."""
        return self.put(f"/todos/{todo_id}", json=payload, headers=headers)

    def delete_todo(self, todo_id: str, headers: Dict[str, str]):
        """Delete a todo."""
        return self.delete(f"/todos/{todo_id}", headers=headers)

    def toggle_todo(self, todo_id: str, payload: Dict[str, Any], headers: Dict[str, str]):
        """Toggle todo completion status."""
        return self.post(f"/todos/{todo_id}/toggle", json=payload, headers=headers)


# Pytest fixture
import pytest


@pytest.fixture
def api_client(client):
    """Create API client wrapper for testing."""
    return APIClient(client)
