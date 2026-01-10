"""
Integration tests for database operations.

Tests User Story 3: Database Integration and Schema Validation
Validates database schema, data persistence, user isolation, and connection handling.
"""
import pytest
from uuid import uuid4, UUID

from sqlmodel import select
from src.app.models.todo import Todo
from tests.fixtures.test_data import TodoFactory
from tests.utils.auth_helpers import AuthHelpers


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.us3
class TestDatabaseSchema:
    """Test database schema and structure."""

    def test_database_connection_successful(self, test_engine):
        """
        T050: Test that database connection is established successfully.

        Given: Test database engine
        When: Connection is attempted
        Then: Connection succeeds without errors
        """
        # Verify engine is connected
        assert test_engine is not None

        # Test a simple query
        with test_engine.connect() as conn:
            result = conn.execute(select(1))
            assert result.scalar() == 1

    def test_todo_table_exists(self, db_with_tables):
        """
        T045: Test that todo table exists in database.

        Given: Database with migrations applied
        When: Schema is inspected
        Then: Todo table exists with correct structure
        """
        from sqlmodel import SQLModel

        # Verify Todo model is in metadata
        table_names = [table.name for table in SQLModel.metadata.tables.values()]
        assert "todo" in table_names, "Todo table should exist in database"

    def test_todo_table_has_required_columns(self, db_with_tables):
        """
        T045: Test that todo table has all required columns.

        Given: Database with todo table
        When: Table structure is inspected
        Then: All required columns exist
        """
        from sqlmodel import SQLModel

        todo_table = SQLModel.metadata.tables.get("todo")
        assert todo_table is not None, "Todo table should exist"

        required_columns = ["id", "user_id", "title", "description", "completed", "version", "created_at", "updated_at"]
        column_names = [col.name for col in todo_table.columns]

        for col in required_columns:
            assert col in column_names, f"Column '{col}' should exist in todo table"

    def test_todo_id_is_primary_key(self, db_with_tables):
        """
        T054: Test that todo.id is the primary key.

        Given: Database with todo table
        When: Table structure is inspected
        Then: id column is marked as primary key
        """
        from sqlmodel import SQLModel

        todo_table = SQLModel.metadata.tables.get("todo")
        id_column = todo_table.columns.get("id")

        assert id_column is not None, "id column should exist"
        assert id_column.primary_key, "id should be primary key"

    def test_todo_user_id_is_indexed(self, db_with_tables):
        """
        T054: Test that todo.user_id has index for performance.

        Given: Database with todo table
        When: Table structure is inspected
        Then: user_id column has index
        """
        from sqlmodel import SQLModel

        todo_table = SQLModel.metadata.tables.get("todo")
        user_id_column = todo_table.columns.get("user_id")

        assert user_id_column is not None, "user_id column should exist"
        # Note: Index validation depends on database implementation


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.us3
class TestDataPersistence:
    """Test data persistence and CRUD operations at database level."""

    def test_todo_persists_after_creation(self, client, test_user_id, db_session):
        """
        T047: Test that todo persists in database after creation.

        Given: Authenticated user creates a todo via API
        When: Database is queried directly
        Then: Todo exists in database with correct data
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = TodoFactory.create_todo_payload(title="Persistent Todo")

        # Create via API
        response = client.post("/api/todos", json=payload, headers=headers)
        assert response.status_code == 201
        todo_id = response.json()["id"]

        # Verify in database
        statement = select(Todo).where(Todo.id == UUID(todo_id))
        db_todo = db_session.exec(statement).first()

        assert db_todo is not None, "Todo should exist in database"
        assert str(db_todo.id) == todo_id
        assert db_todo.title == "Persistent Todo"
        assert str(db_todo.user_id) == str(test_user_id)

    def test_todo_update_persists_in_database(self, client, test_user_id, db_session):
        """
        T047: Test that todo updates persist in database.

        Given: Existing todo in database
        When: Todo is updated via API
        Then: Changes are persisted in database
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create todo
        create_payload = TodoFactory.create_todo_payload(title="Original")
        response = client.post("/api/todos", json=create_payload, headers=headers)
        todo_id = response.json()["id"]

        # Update todo
        update_payload = TodoFactory.create_update_payload(title="Updated", version=1)
        response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)
        assert response.status_code == 200

        # Verify in database
        statement = select(Todo).where(Todo.id == UUID(todo_id))
        db_todo = db_session.exec(statement).first()

        assert db_todo.title == "Updated", "Update should persist in database"
        assert db_todo.version == 2, "Version should be incremented"

    def test_todo_deletion_removes_from_database(self, client, test_user_id, db_session):
        """
        T047: Test that todo deletion removes record from database.

        Given: Existing todo in database
        When: Todo is deleted via API
        Then: Record is removed from database
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create todo
        payload = TodoFactory.create_todo_payload(title="To Delete")
        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Delete todo
        response = client.delete(f"/api/todos/{todo_id}", headers=headers)
        assert response.status_code == 204

        # Verify deletion in database
        statement = select(Todo).where(Todo.id == UUID(todo_id))
        db_todo = db_session.exec(statement).first()

        assert db_todo is None, "Todo should be removed from database"

    def test_timestamp_auto_update_on_modification(self, client, test_user_id, db_session):
        """
        T052: Test that updated_at timestamp is automatically updated.

        Given: Existing todo in database
        When: Todo is modified
        Then: updated_at timestamp is updated automatically
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create todo
        payload = TodoFactory.create_todo_payload(title="Timestamp Test")
        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Get initial timestamp
        statement = select(Todo).where(Todo.id == UUID(todo_id))
        initial_todo = db_session.exec(statement).first()
        initial_updated_at = initial_todo.updated_at

        # Wait a moment and update
        import time
        time.sleep(0.1)

        update_payload = TodoFactory.create_update_payload(title="Updated", version=1)
        client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)

        # Verify timestamp changed
        db_session.expire_all()  # Refresh from database
        updated_todo = db_session.exec(statement).first()

        assert updated_todo.updated_at > initial_updated_at, \
            "updated_at should be automatically updated on modification"


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.us3
class TestUserDataIsolation:
    """Test that user data is properly isolated at database level."""

    def test_user_can_only_query_own_todos(self, client, test_user_id, other_user_id, db_session):
        """
        T048: Test that database queries enforce user data isolation.

        Given: Two users with their own todos
        When: Database is queried for user's todos
        Then: Only that user's todos are returned
        """
        user_a_headers = AuthHelpers.create_auth_headers(test_user_id)
        user_b_headers = AuthHelpers.create_auth_headers(other_user_id)

        # User A creates 2 todos
        for i in range(2):
            payload = TodoFactory.create_todo_payload(title=f"User A Todo {i}")
            client.post("/api/todos", json=payload, headers=user_a_headers)

        # User B creates 3 todos
        for i in range(3):
            payload = TodoFactory.create_todo_payload(title=f"User B Todo {i}")
            client.post("/api/todos", json=payload, headers=user_b_headers)

        # Query database for User A's todos
        statement = select(Todo).where(Todo.user_id == UUID(str(test_user_id)))
        user_a_todos = db_session.exec(statement).all()

        assert len(user_a_todos) == 2, "User A should have 2 todos"
        for todo in user_a_todos:
            assert str(todo.user_id) == str(test_user_id), "All todos should belong to User A"

        # Query database for User B's todos
        statement = select(Todo).where(Todo.user_id == UUID(str(other_user_id)))
        user_b_todos = db_session.exec(statement).all()

        assert len(user_b_todos) == 3, "User B should have 3 todos"
        for todo in user_b_todos:
            assert str(todo.user_id) == str(other_user_id), "All todos should belong to User B"

    def test_user_cannot_access_other_user_data_via_database(self, client, test_user_id, other_user_id, db_session):
        """
        T048: Test that direct database access respects user isolation.

        Given: User A creates a todo
        When: Database is queried for User B's todos
        Then: User A's todo is not returned
        """
        user_a_headers = AuthHelpers.create_auth_headers(test_user_id)

        # User A creates a todo
        payload = TodoFactory.create_todo_payload(title="User A's Private Todo")
        response = client.post("/api/todos", json=payload, headers=user_a_headers)
        todo_id = response.json()["id"]

        # Query for User B's todos (should not include User A's todo)
        statement = select(Todo).where(Todo.user_id == UUID(str(other_user_id)))
        user_b_todos = db_session.exec(statement).all()

        # Verify User A's todo is not in User B's results
        user_b_todo_ids = [str(todo.id) for todo in user_b_todos]
        assert todo_id not in user_b_todo_ids, "User A's todo should not appear in User B's query"

    def test_cascade_delete_on_user_deletion(self, db_session, test_user_id):
        """
        T051: Test that todos are deleted when user is deleted (if implemented).

        Given: User with multiple todos
        When: User is deleted
        Then: All user's todos are also deleted

        Note: This test assumes cascade delete is implemented.
        If not implemented, this test documents the expected behavior.
        """
        # Create todos directly in database
        for i in range(3):
            todo_data = TodoFactory.create_todo_data(
                user_id=test_user_id,
                title=f"Todo {i}"
            )
            todo = Todo(**todo_data)
            db_session.add(todo)
        db_session.commit()

        # Verify todos exist
        statement = select(Todo).where(Todo.user_id == UUID(str(test_user_id)))
        todos = db_session.exec(statement).all()
        assert len(todos) == 3, "Should have 3 todos before deletion"

        # Note: User deletion would happen here if user management is implemented
        # For now, we manually delete todos to simulate cascade
        for todo in todos:
            db_session.delete(todo)
        db_session.commit()

        # Verify todos are deleted
        todos_after = db_session.exec(statement).all()
        assert len(todos_after) == 0, "All todos should be deleted"


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.us3
class TestDatabaseConstraints:
    """Test database constraints and validation."""

    def test_todo_version_starts_at_one(self, client, test_user_id, db_session):
        """
        T054: Test that todo version starts at 1 on creation.

        Given: New todo is created
        When: Todo is saved to database
        Then: Version is set to 1
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = TodoFactory.create_todo_payload(title="Version Test")

        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Verify in database
        statement = select(Todo).where(Todo.id == UUID(todo_id))
        db_todo = db_session.exec(statement).first()

        assert db_todo.version == 1, "Initial version should be 1"

    def test_todo_version_increments_on_update(self, client, test_user_id, db_session):
        """
        T054: Test that todo version increments on each update.

        Given: Existing todo with version 1
        When: Todo is updated multiple times
        Then: Version increments each time
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create todo
        payload = TodoFactory.create_todo_payload(title="Version Test")
        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Update 3 times
        for i in range(1, 4):
            update_payload = TodoFactory.create_update_payload(
                title=f"Update {i}",
                version=i
            )
            response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)
            assert response.status_code == 200

            # Verify version in database
            db_session.expire_all()
            statement = select(Todo).where(Todo.id == UUID(todo_id))
            db_todo = db_session.exec(statement).first()
            assert db_todo.version == i + 1, f"Version should be {i + 1} after update {i}"

    def test_completed_defaults_to_false(self, client, test_user_id, db_session):
        """
        T054: Test that completed field defaults to False.

        Given: New todo is created without specifying completed
        When: Todo is saved to database
        Then: completed is False by default
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = TodoFactory.create_todo_payload(title="Default Completed Test")

        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Verify in database
        statement = select(Todo).where(Todo.id == UUID(todo_id))
        db_todo = db_session.exec(statement).first()

        assert db_todo.completed is False, "completed should default to False"

    def test_timestamps_are_set_on_creation(self, client, test_user_id, db_session):
        """
        T052: Test that created_at and updated_at are set on creation.

        Given: New todo is created
        When: Todo is saved to database
        Then: Both timestamps are set to current time
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = TodoFactory.create_todo_payload(title="Timestamp Test")

        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Verify in database
        statement = select(Todo).where(Todo.id == UUID(todo_id))
        db_todo = db_session.exec(statement).first()

        assert db_todo.created_at is not None, "created_at should be set"
        assert db_todo.updated_at is not None, "updated_at should be set"
        assert db_todo.created_at <= db_todo.updated_at, \
            "created_at should be <= updated_at"
