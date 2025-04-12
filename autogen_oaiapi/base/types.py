from pydantic import BaseModel
from typing import List, Optional, Literal, Union

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: Union[str, None]

class ChatCompletionRequest(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    model: Optional[str] = None

class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = "stop"

class ChatCompletionResponse(BaseModel):
    id: str = "chatcmpl-xxx"
    object: str = "chat.completion"
    choices: List[ChatCompletionResponseChoice]
    usage: Optional[dict] = None