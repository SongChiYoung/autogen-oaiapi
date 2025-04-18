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
    terminate_texts = server.terminate_messages
    llm_messages = convert_to_llm_messages(body.messages)
    len_llm_messages = len(llm_messages)
    request_model = body.model
    is_stream = body.stream
    
    if is_stream:
        # Streaming response: response AsyncGenerator wrapping by StreamingResponse
        result = team.run_stream(task=llm_messages)
        response = await build_openai_response(request_model, result, terminate_texts, idx, source, is_stream=is_stream, previous_messages=len_llm_messages)
        if isinstance(response, AsyncGenerator):
             return StreamingResponse(response, media_type="text/event-stream")
        else:
             # TODO: right formatting for error response
             return {"error": "Failed to generate stream"}, 500
    else:
        # Non-streaming response: returning the response directly
        result = await team.run(task=llm_messages)
        response = await build_openai_response(request_model, result, terminate_texts, idx, source, is_stream=is_stream, previous_messages=len_llm_messages)
        if isinstance(response, ChatCompletionResponse):
            return response
        else:
             # TODO: right formatting for error response
            return {"error": "Failed to generate completion"}, 500