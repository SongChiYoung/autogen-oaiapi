from pydantic import BaseModel
from typing import List, Optional
from autogen_oaiapi.base.types._chat_message import ChatCompletionMessage


class ModelResponse(BaseModel):
    """
    Represents a model metadata response.

    Args:
        id (str): Model identifier.
        object (str): Object type.
        created (int): Creation timestamp.
        owned_by (str): Owner of the model.
    """
    id: str
    object: str
    created: int
    owned_by: str

class ModelListResponse(BaseModel):
    """
    Response model for a list of available models.

    Args:
        data (List[ModelResponse]): List of model metadata.
        object (str): Object type.
    """
    data: List[ModelResponse]
    object: str

class ModelListRequest(BaseModel):
    """
    Request model for listing or querying models.

    Args:
        model (str): Model name to query.
        messages (List[ChatMessage]): List of chat messages.
        stream (bool, optional): Whether to stream the response.
        temperature (float, optional): Sampling temperature.
        top_p (float, optional): Nucleus sampling parameter.
        n (int, optional): Number of completions to generate.
        stop (List[str], optional): Stop sequences.
        max_tokens (int, optional): Maximum number of tokens.
    """
    model: str
    messages: List[ChatCompletionMessage]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = 1000