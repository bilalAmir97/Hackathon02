"""Unit tests for agent orchestration use case.

Tests the agent orchestration logic that coordinates between the agent,
MCP tools, and conversation persistence.
Following TDD approach - these tests should fail until orchestration is implemented.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4


@pytest.fixture
def mock_agent_factory():
    """Create mock agent factory."""
    with patch('src.use_cases.agent_orchestration.AgentFactory') as mock:
        yield mock


@pytest.fixture
def mock_mcp_adapter():
    """Create mock MCP adapter."""
    with patch('src.use_cases.agent_orchestration.MCPAdapter') as mock:
        yield mock


@pytest.mark.asyncio
async def test_orchestration_detects_create_intent():
    """Test that orchestration detects 'create' or 'add' intent in user message.
    
    This tests intent detection for task creation requests.
    """
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    messages = [
        "Create a task to buy groceries",
        "Add a task for meeting",
        "Make a new task",
        "I need to create a task"
    ]
    
    # Act & Assert
    for message in messages:
        intent = orchestration._detect_intent(message)
        assert intent in ['create', 'add'], f"Should detect create/add intent in: {message}"


@pytest.mark.asyncio
async def test_orchestration_calls_add_task_tool():
    """Test that orchestration calls add_task tool for create intent.
    
    This tests that the agent correctly invokes the add_task MCP tool.
    """
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Create a task to buy groceries"
    
    # Mock the agent response with tool call
    mock_agent_response = {
        'content': "I'll create that task for you.",
        'tool_calls': [
            {
                'name': 'add_task',
                'arguments': {'title': 'Buy groceries', 'description': None}
            }
        ]
    }
    
    # Act
    with patch.object(orchestration, '_call_agent', return_value=mock_agent_response):
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {'id': '123', 'title': 'Buy groceries', 'status': 'pending'}
            
            result = await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=None
            )
            
            # Assert
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            assert call_args[1]['tool_name'] == 'add_task'
            assert 'groceries' in call_args[1]['parameters']['title'].lower()


@pytest.mark.asyncio
async def test_orchestration_returns_tool_call_transparency():
    """Test that orchestration returns tool calls with full transparency.
    
    This tests that tool_calls array includes all required fields for auditability.
    """
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Create a task"
    
    # Mock successful tool execution
    mock_tool_result = {
        'id': '123',
        'title': 'Test task',
        'status': 'pending'
    }
    
    # Act
    with patch.object(orchestration, '_call_agent') as mock_agent:
        mock_agent.return_value = {
            'content': "Task created",
            'tool_calls': [{'name': 'add_task', 'arguments': {'title': 'Test task'}}]
        }
        
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = mock_tool_result
            
            result = await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=None
            )
            
            # Assert
            assert 'tool_calls' in result
            assert len(result['tool_calls']) > 0
            
            tool_call = result['tool_calls'][0]
            # Verify required transparency fields
            assert 'tool_name' in tool_call
            assert 'input_parameters' in tool_call
            assert 'output_result' in tool_call
            assert 'execution_status' in tool_call
            assert 'timestamp' in tool_call


@pytest.mark.asyncio
async def test_orchestration_creates_conversation_if_missing():
    """Test that orchestration creates new conversation when conversation_id is None."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Hello"
    
    # Act
    with patch.object(orchestration, '_create_conversation', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = 1  # conversation_id
        
        with patch.object(orchestration, '_call_agent') as mock_agent:
            mock_agent.return_value = {'content': 'Hi!', 'tool_calls': []}
            
            with patch.object(orchestration, '_persist_messages', new_callable=AsyncMock):
                result = await orchestration.process_message(
                    user_id=user_id,
                    message=message,
                    conversation_id=None
                )
                
                # Assert
                mock_create.assert_called_once_with(user_id)
                assert result['conversation_id'] == 1


@pytest.mark.asyncio
async def test_orchestration_fetches_history_for_existing_conversation():
    """Test that orchestration fetches conversation history when resuming."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    conversation_id = 1
    message = "What tasks do I have?"
    
    # Mock conversation history
    mock_history = [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi! How can I help?'}
    ]
    
    # Act
    with patch.object(orchestration, '_fetch_conversation_history', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_history
        
        with patch.object(orchestration, '_call_agent') as mock_agent:
            mock_agent.return_value = {'content': 'You have 0 tasks', 'tool_calls': []}
            
            with patch.object(orchestration, '_persist_messages', new_callable=AsyncMock):
                await orchestration.process_message(
                    user_id=user_id,
                    message=message,
                    conversation_id=conversation_id
                )
                
                # Assert
                mock_fetch.assert_called_once_with(conversation_id)
                # Verify history was passed to agent
                agent_call_args = mock_agent.call_args
                assert len(agent_call_args[0]) > 0 or 'history' in agent_call_args[1]


@pytest.mark.asyncio
async def test_orchestration_validates_conversation_ownership():
    """Test that orchestration validates user owns the conversation."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    different_user_id = uuid4()
    conversation_id = 1
    message = "Hello"
    
    # Act & Assert
    with patch.object(orchestration, '_validate_conversation_ownership', new_callable=AsyncMock) as mock_validate:
        mock_validate.side_effect = PermissionError("Conversation does not belong to user")
        
        with pytest.raises(PermissionError):
            await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=conversation_id
            )


@pytest.mark.asyncio
async def test_orchestration_persists_user_and_assistant_messages():
    """Test that orchestration persists both user and assistant messages."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Create a task"
    
    # Act
    with patch.object(orchestration, '_create_conversation', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = 1
        
        with patch.object(orchestration, '_call_agent') as mock_agent:
            mock_agent.return_value = {'content': 'Task created', 'tool_calls': []}
            
            with patch.object(orchestration, '_persist_messages', new_callable=AsyncMock) as mock_persist:
                await orchestration.process_message(
                    user_id=user_id,
                    message=message,
                    conversation_id=None
                )
                
                # Assert
                mock_persist.assert_called_once()
                call_args = mock_persist.call_args
                messages = call_args[0][1]  # Second argument is messages list
                
                # Should have user message and assistant message
                assert len(messages) == 2
                assert messages[0]['role'] == 'user'
                assert messages[0]['content'] == message
                assert messages[1]['role'] == 'assistant'


@pytest.mark.asyncio
async def test_orchestration_handles_tool_execution_errors():
    """Test that orchestration handles tool execution errors gracefully."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Create a task"
    
    # Act
    with patch.object(orchestration, '_call_agent') as mock_agent:
        mock_agent.return_value = {
            'content': 'Creating task',
            'tool_calls': [{'name': 'add_task', 'arguments': {'title': 'Test'}}]
        }
        
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Database error")
            
            with patch.object(orchestration, '_create_conversation', new_callable=AsyncMock):
                with patch.object(orchestration, '_persist_messages', new_callable=AsyncMock):
                    result = await orchestration.process_message(
                        user_id=user_id,
                        message=message,
                        conversation_id=None
                    )
                    
                    # Assert - should return error in tool_calls
                    assert 'tool_calls' in result
                    tool_call = result['tool_calls'][0]
                    assert tool_call['execution_status'] == 'error'
                    assert 'error_message' in tool_call


# User Story 2: List Tasks Intent Tests

@pytest.mark.asyncio
async def test_orchestration_detects_list_intent():
    """Test that orchestration detects 'list' or 'show' intent in user message."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    messages = [
        "Show me my tasks",
        "List all tasks",
        "What tasks do I have?",
        "Display my tasks",
        "View my pending tasks"
    ]
    
    # Act & Assert
    for message in messages:
        intent = orchestration._detect_intent(message)
        assert intent == 'list', f"Should detect list intent in: {message}"


@pytest.mark.asyncio
async def test_orchestration_calls_list_tasks_tool():
    """Test that orchestration calls list_tasks tool for list intent."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Show me my tasks"
    
    # Mock the agent response with tool call
    mock_agent_response = {
        'content': "Here are your tasks.",
        'tool_calls': [
            {
                'name': 'list_tasks',
                'arguments': {}
            }
        ]
    }
    
    # Act
    with patch.object(orchestration, '_call_agent', return_value=mock_agent_response):
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {'tasks': [], 'count': 0}
            
            result = await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=None
            )
            
            # Assert
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            assert call_args[1]['tool_name'] == 'list_tasks'


@pytest.mark.asyncio
async def test_orchestration_list_tasks_with_status_filter():
    """Test that orchestration passes status filter to list_tasks."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Show me my pending tasks"
    
    # Mock agent response with status filter
    mock_agent_response = {
        'content': "Here are your pending tasks.",
        'tool_calls': [
            {
                'name': 'list_tasks',
                'arguments': {'status': 'pending'}
            }
        ]
    }
    
    # Act
    with patch.object(orchestration, '_call_agent', return_value=mock_agent_response):
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {'tasks': [], 'count': 0}
            
            await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=None
            )
            
            # Assert
            call_args = mock_execute.call_args
            assert call_args[1]['parameters'].get('status') == 'pending'


@pytest.mark.asyncio
async def test_orchestration_handles_empty_task_list():
    """Test that orchestration handles empty task list gracefully."""
    from src.use_cases.agent_orchestration import AgentOrchestration
    
    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Show me my tasks"
    
    # Mock empty result
    mock_agent_response = {
        'content': "You don't have any tasks yet.",
        'tool_calls': [
            {
                'name': 'list_tasks',
                'arguments': {}
            }
        ]
    }
    
    # Act
    with patch.object(orchestration, '_call_agent', return_value=mock_agent_response):
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {'tasks': [], 'count': 0}
            
            result = await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=None
            )
            
            # Assert
            assert 'tool_calls' in result
            tool_call = result['tool_calls'][0]
            assert tool_call['execution_status'] == 'success'
            assert tool_call['output_result']['count'] == 0


# User Story 3: Update Task Intent Tests

@pytest.mark.asyncio
async def test_orchestration_detects_update_intent():
    """Test that orchestration detects 'update' or 'rename' intent in user message."""
    from src.use_cases.agent_orchestration import AgentOrchestration

    # Arrange
    orchestration = AgentOrchestration()
    messages = [
        "Rename task to new title",
        "Update the task",
        "Change task title",
        "Modify the task",
        "Edit task description"
    ]

    # Act & Assert
    for message in messages:
        intent = orchestration._detect_intent(message)
        assert intent == 'update', f"Should detect update intent in: {message}"


@pytest.mark.asyncio
async def test_orchestration_calls_update_task_tool():
    """Test that orchestration calls update_task tool for update intent."""
    from src.use_cases.agent_orchestration import AgentOrchestration

    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    task_id = str(uuid4())
    message = f"Rename task {task_id} to buy organic milk"

    # Mock the agent response with tool call
    mock_agent_response = {
        'content': "I'll update that task for you.",
        'tool_calls': [
            {
                'name': 'update_task',
                'arguments': {
                    'task_id': task_id,
                    'title': 'buy organic milk',
                    'description': None
                }
            }
        ]
    }

    # Act
    with patch.object(orchestration, '_call_agent', return_value=mock_agent_response):
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                'id': task_id,
                'title': 'buy organic milk',
                'status': 'pending'
            }

            result = await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=None
            )

            # Assert
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            assert call_args[1]['tool_name'] == 'update_task'
            assert call_args[1]['parameters']['task_id'] == task_id
            assert 'organic milk' in call_args[1]['parameters']['title'].lower()


@pytest.mark.asyncio
async def test_orchestration_update_with_description():
    """Test that orchestration can update both title and description."""
    from src.use_cases.agent_orchestration import AgentOrchestration

    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    task_id = str(uuid4())
    message = f"Update task {task_id} with title 'New Title' and description 'New Description'"

    # Mock the agent response
    mock_agent_response = {
        'content': "Task updated successfully.",
        'tool_calls': [
            {
                'name': 'update_task',
                'arguments': {
                    'task_id': task_id,
                    'title': 'New Title',
                    'description': 'New Description'
                }
            }
        ]
    }

    # Act
    with patch.object(orchestration, '_call_agent', return_value=mock_agent_response):
        with patch.object(orchestration, '_execute_tool_call', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                'id': task_id,
                'title': 'New Title',
                'description': 'New Description',
                'status': 'pending'
            }

            result = await orchestration.process_message(
                user_id=user_id,
                message=message,
                conversation_id=None
            )

            # Assert
            call_args = mock_execute.call_args
            assert call_args[1]['parameters']['title'] == 'New Title'
            assert call_args[1]['parameters']['description'] == 'New Description'


@pytest.mark.asyncio
async def test_orchestration_handles_ambiguous_task_reference():
    """Test that orchestration handles ambiguous task references gracefully.

    When user says 'update the task' without specifying which one,
    the agent should ask for clarification.
    """
    from src.use_cases.agent_orchestration import AgentOrchestration

    # Arrange
    orchestration = AgentOrchestration()
    user_id = uuid4()
    message = "Rename the task to new title"  # Ambiguous - which task?

    # Mock the agent response asking for clarification
    mock_agent_response = {
        'content': "Which task would you like to rename? Please provide the task ID or more details.",
        'tool_calls': []  # No tool call when ambiguous
    }

    # Act
    with patch.object(orchestration, '_call_agent', return_value=mock_agent_response):
        result = await orchestration.process_message(
            user_id=user_id,
            message=message,
            conversation_id=None
        )

        # Assert
        assert 'tool_calls' in result
        assert len(result['tool_calls']) == 0  # No tool executed
        assert 'which task' in result['response'].lower() or 'task id' in result['response'].lower()

