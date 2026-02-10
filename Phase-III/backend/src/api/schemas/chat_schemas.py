"""Chat endpoint request/response schemas.

Defines Pydantic models for the chat endpoint that handles conversational
AI interactions with tool call transparency.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request schema for chat endpoint.
    
    Attributes:
        message: User's message text (required)
        conversation_id: Optional conversation ID to resume existing conversation
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's message text",
        examples=["Create a task to buy groceries"]
    )

    conversation_id: int | None = Field(
        default=None,
        description="Optional conversation ID to resume existing conversation",
        examples=[1, 42]
    )

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Validate message is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ToolCall(BaseModel):
    """Tool call transparency schema."""

    tool_name: str
    input_parameters: dict[str, Any]
    output_result: dict[str, Any]
    execution_status: str
    error_message: str | None = None
    timestamp: str


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: int
    response: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
