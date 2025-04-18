from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
import uuid
import time


class ChatMessage(BaseModel):
    """
    Represents a single chat message with a role and content.

    Args:
        role (Literal["user", "assistant", "system"]): The role of the message sender.
        content (str | None): The message content.
    """
    role: Literal["user", "assistant", "system"]
    content: Union[str, None]

class ChatCompletionRequest(BaseModel):
    """
    Request model for chat completion API.

    Args:
        session_id (str, optional): Session identifier.
        messages (List[ChatMessage]): List of chat messages.
        stream (bool, optional): Whether to stream the response.
        model (str, optional): Model name to use.
    """
    session_id: Optional[str] = None
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    model: Optional[str] = None

class ChatCompletionResponseChoice(BaseModel):
    """
    Represents a single choice in the chat completion response.

    Args:
        index (int): Index of the choice.
        message (ChatMessage): The message for this choice.
        finish_reason (str, optional): Reason for finishing.
    """
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = "stop"

class UsageInfo(BaseModel):
    """
    Token usage statistics for a chat completion response.

    Args:
        prompt_tokens (int): Number of prompt tokens used.
        completion_tokens (int): Number of completion tokens used.
        total_tokens (int): Total tokens used.
    """
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    """
    Response model for chat completion API.

    Args:
        id (str): Unique response identifier.
        object (str): Object type (default: "chat.completion").
        created (int): Timestamp of creation.
        model (str): Model name.
        choices (List[ChatCompletionResponseChoice]): List of response choices.
        usage (UsageInfo): Token usage information.
    """
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}") # build uuid for id
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time())) # build timestamp for created
    model: str # model name is passed from request
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo

class DeltaMessage(BaseModel):
    """
    Represents a delta (partial) message for streaming responses.

    Args:
        role (Literal["assistant"], optional): Role of the sender.
        content (str, optional): Partial message content.
    """
    role: Optional[Literal["assistant"]] = None
    content: Optional[str] = None

class ChatCompletionStreamChoice(BaseModel):
    """
    Represents a single choice in a streaming chat completion response.

    Args:
        index (int): Index of the choice.
        delta (DeltaMessage): Delta message for this choice.
        finish_reason (str, optional): Reason for finishing.
    """
    index: int
    delta: DeltaMessage
    finish_reason: Optional[str] = None

class ChatCompletionStreamResponse(BaseModel):
    """
    Streaming response model for chat completion API.

    Args:
        id (str): Unique response identifier.
        object (str): Object type (default: "chat.completion.chunk").
        created (int): Timestamp of creation.
        model (str): Model name.
        choices (List[ChatCompletionStreamChoice]): List of streaming choices.
        usage (UsageInfo, optional): Token usage information.
    """
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionStreamChoice]
    usage: Optional[UsageInfo] = None