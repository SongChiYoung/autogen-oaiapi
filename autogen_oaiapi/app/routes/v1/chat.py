from typing import AsyncGenerator, Coroutine, Any
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from autogen_oaiapi.base.types import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionErrorResponse,
    ChatCompletionErrorDetail,
)
from autogen_oaiapi.message.message_converter import convert_to_llm_messages
from autogen_oaiapi.message.response_builder import build_openai_response
from autogen_oaiapi.model import Model
from ....base.types import ReturnMessage


router = APIRouter()

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: Request,
    body: ChatCompletionRequest
) -> ChatCompletionResponse | StreamingResponse | ChatCompletionErrorResponse:
    """
    Handle chat completion requests for the OpenAI-compatible API.

    Args:
        request (Request): The FastAPI request object.
        body (ChatCompletionRequest): The chat completion request payload.

    Returns:
        ChatCompletionResponse | StreamingResponse | dict: The chat completion response, streaming response, or error dict.

    Raises:
        500: If the completion or stream generation fails.
    """
    server = request.app.state.server
    llm_messages = convert_to_llm_messages(body.messages)
    request_model = body.model
    is_stream: bool = body.stream or False
    
    if request_model is None:
        request_model = "autogen-baseteam"
    
    model: Model|None  = server.model
    if model is None:
        return ChatCompletionErrorResponse(
            error=ChatCompletionErrorDetail(
                message="Model not found",
                type="invalid_request_error",
                param="model",
                code="model_not_found"
            )
        )

    result: AsyncGenerator[ReturnMessage, None] | Coroutine[Any, Any, ReturnMessage]
    if is_stream:
        result = model.run_stream(name=request_model, messages=llm_messages)
        response = await build_openai_response(request_model, result, is_stream=is_stream)
        if isinstance(response, AsyncGenerator):
             # server.cleanup_team(body.session_id, team)
             return StreamingResponse(response, media_type="text/event-stream")
        else:
             # server.cleanup_team(body.session_id, team)
             return ChatCompletionErrorResponse(
                error=ChatCompletionErrorDetail(
                    message="Failed to generate completion",
                    type="server_error",
                    param=None,
                    code="server_error"
                )
             )
    else:
        # Non-streaming response: returning the response directly
        result = model.run(name=request_model, messages=llm_messages)
        response = await build_openai_response(request_model, result, is_stream=is_stream)
        if isinstance(response, ChatCompletionResponse):
            # server.cleanup_team(body.session_id, team)
            return response
        else:
            # server.cleanup_team(body.session_id, team)
            return ChatCompletionErrorResponse(
                error=ChatCompletionErrorDetail(
                    message="Failed to generate completion",
                    type="server_error",
                    param=None,
                    code="server_error"
                )
            )