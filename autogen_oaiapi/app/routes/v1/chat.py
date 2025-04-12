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
    print("========================")
    print(body)
    print("========================")
    request_model = body.model
    is_stream = body.stream
    result = await team.run(task=llm_messages)
    # result = result.messages[-idx]
    response = await build_openai_response(request_model, result, terminate_text, idx, source, is_stream=is_stream)

    print(f"response: {response}")

    if is_stream:
        # 스트리밍 응답: 반환된 비동기 제너레이터를 StreamingResponse 로 감싸서 반환
        if isinstance(response, AsyncGenerator):
             # 주의: response_data는 제너레이터 함수이므로 호출해서 이터레이터를 얻어야 함
             return StreamingResponse(response, media_type="text/event-stream")
        else:
             # 예외 처리: 스트리밍 요청인데 제너레이터가 반환되지 않은 경우
             return {"error": "Failed to generate stream"}, 500
    else:
        # 비-스트리밍 응답: 반환된 ChatCompletionResponse 객체 반환 (FastAPI가 JSON으로 변환)
        if isinstance(response, ChatCompletionResponse):
            return response
        else:
            # 예외 처리: 비-스트리밍 요청인데 잘못된 타입이 반환된 경우
            return {"error": "Failed to generate completion"}, 500