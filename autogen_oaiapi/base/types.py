from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
import uuid
import time

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: Union[str, None]

class ChatCompletionRequest(BaseModel):
    session_id: Optional[str] = None
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    model: Optional[str] = None

class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = "stop"

class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}") # 고유 ID 자동 생성
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time())) # 현재 Unix 타임스탬프 자동 생성
    model: str # 모델명은 응답 생성 시 명시적으로 전달받아야 함
    choices: List[ChatCompletionResponseChoice]
    usage: UsageInfo # UsageInfo 모델 사용



# openai style model req/res
class ModelResponse(BaseModel):
    id: str
    object: str
    created: int
    owned_by: str

class ModelListResponse(BaseModel):
    data: List[ModelResponse]
    object: str

class ModelListRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = 1000