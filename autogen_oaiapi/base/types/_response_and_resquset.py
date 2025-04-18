from pydantic import BaseModel
from typing import List, Optional
from autogen_oaiapi.base.types._chat_message import ChatMessage


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