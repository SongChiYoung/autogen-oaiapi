from typing import AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from autogen_oaiapi.base.types import ChatCompletionRequest, ChatCompletionResponse
from autogen_oaiapi.message.message_converter import convert_to_llm_messages
from autogen_oaiapi.message.response_builder import build_openai_response

router = APIRouter()

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: Request, body: ChatCompletionRequest):
    server = request.app.state.server
    team = await server.get_team(body.session_id)
    idx = server.output_idx
    source = server.source_select
    terminate_text = server.terminate_message
    llm_messages = convert_to_llm_messages(body.messages)
    request_model = body.model
    is_stream = body.stream
    result = await team.run(task=llm_messages)
    response = await build_openai_response(request_model, result, terminate_text, idx, source, is_stream=is_stream)

    if is_stream:
        # Streaming response: response AsyncGenerator wrapping by StreamingResponse
        if isinstance(response, AsyncGenerator):
             return StreamingResponse(response, media_type="text/event-stream")
        else:
             # TODO: right formatting for error response
             return {"error": "Failed to generate stream"}, 500
    else:
        # Non-streaming response: returning the response directly
        if isinstance(response, ChatCompletionResponse):
            return response
        else:
             # TODO: right formatting for error response
            return {"error": "Failed to generate completion"}, 500