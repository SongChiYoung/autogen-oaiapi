import asyncio
from typing import AsyncGenerator
import time
import uuid
from autogen_oaiapi.base.types import (
    ChatMessage,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    UsageInfo,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    DeltaMessage,
)

async def build_openai_response(model_name, result, trminate_text = "", idx=None, source=None, is_stream=False):
    if idx is None and source is None:
        idx = 0
    if idx is not None and source is not None:
        raise ValueError("Either idx or source must be provided, not both.")
    if model_name is None:
        model_name = "autogen"

    total_prompt_tokens = 0
    total_completion_tokens = 0

    # print(f"result: {result}")
    result_message=None

    for message in result.messages:
        if tokens:=message.models_usage:
            total_prompt_tokens += tokens.prompt_tokens
            total_completion_tokens += tokens.completion_tokens
        if source is not None:
            if message.source == source:
                result_message = message
    total_tokens = total_prompt_tokens + total_completion_tokens

    if idx is not None:
        result_message = result.messages[-idx]

    if result_message is None:
        content = ""
    else:
        content = result_message.content

    content = content.replace(trminate_text, "")

    if not is_stream:
        response = ChatCompletionResponse(
            # id, created는 Field default_factory 에서 자동 생성됨
            model=model_name, # 실제 사용된 모델명 전달
            choices=[
                ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role= 'assistant', content=content), # LLM 결과 메시지
                    finish_reason="stop" # 종료 사유
                )
            ],
            usage=UsageInfo( # UsageInfo 모델로 생성
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                total_tokens=total_tokens
            )
        )
        return response
    
    else:
        # 스트리밍: SSE 형식 문자열을 yield 하는 비동기 제너레이터 반환
        async def _stream_generator() -> AsyncGenerator[str, None]:
            request_id = f"chatcmpl-{uuid.uuid4().hex}"
            created_timestamp = int(time.time())

            # 1. 초기 청크 (role)
            initial_chunk = ChatCompletionStreamResponse(
                id=request_id,
                model=model_name,
                created=created_timestamp,
                choices=[
                    ChatCompletionStreamChoice(
                        index=0,
                        delta=DeltaMessage(role="assistant"),
                        finish_reason=None
                    )
                ]
            )
            yield f"data: {initial_chunk.model_dump_json()}\n\n"
            await asyncio.sleep(0.01) # 클라이언트 처리 시간 확보

            # 2. 내용 청크 (전체 내용을 한 번에)
            if content: # 내용이 있을 때만 전송
                content_chunk = ChatCompletionStreamResponse(
                    id=request_id,
                    model=model_name,
                    created=int(time.time()), # 생성 시간 갱신 가능
                    choices=[
                        ChatCompletionStreamChoice(
                            index=0,
                            delta=DeltaMessage(content=content),
                            finish_reason=None
                        )
                    ]
                )
                yield f"data: {content_chunk.model_dump_json()}\n\n"
                await asyncio.sleep(0.01)

            # 3. 종료 청크
            final_chunk = ChatCompletionStreamResponse(
                id=request_id,
                model=model_name,
                created=int(time.time()),
                choices=[
                    ChatCompletionStreamChoice(
                        index=0,
                        delta=DeltaMessage(), # 빈 델타
                        finish_reason="stop" # 종료 사유
                    )
                ]
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"

            # 4. 스트림 종료 메시지
            yield "data: [DONE]\n\n"

        # 비동기 제너레이터 함수 자체를 반환
        return _stream_generator()