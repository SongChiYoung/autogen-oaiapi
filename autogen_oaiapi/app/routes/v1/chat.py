from typing import AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from autogen_oaiapi.base.types import ChatCompletionRequest, ChatCompletionResponse
from autogen_oaiapi.message.message_converter import convert_to_llm_messages
from autogen_oaiapi.message.response_builder import build_openai_response

router = APIRouter()

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: Request, body: ChatCompletionRequest):
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
    is_stream = body.stream
    
    if request_model is None:
        request_model = "autogen-baseteam"
    
    model = server.model
    if model is None:
        return {"error": f"Model '{request_model}' not found"}, 404

    if is_stream:
        result = model.run_stream(name=request_model, messages=llm_messages)
        response = await build_openai_response(request_model, result, is_stream=is_stream)
        if isinstance(response, AsyncGenerator):
             # server.cleanup_team(body.session_id, team)
             return StreamingResponse(response, media_type="text/event-stream")
        else:
             # TODO: right formatting for error response
             # server.cleanup_team(body.session_id, team)
             return {"error": "Failed to generate stream"}, 500        
    else:
        # Non-streaming response: returning the response directly
        result = model.run(name=request_model, messages=llm_messages)
        response = await build_openai_response(request_model, result, is_stream=is_stream)
        if isinstance(response, ChatCompletionResponse):
            # server.cleanup_team(body.session_id, team)
            return response
        else:
             # TODO: right formatting for error response
            # server.cleanup_team(body.session_id, team)
            return {"error": "Failed to generate completion"}, 500