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

async def build_openai_response(model_name, result, terminate_text = "", idx=None, source=None, is_stream=False):
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

    content = content.replace(terminate_text, "")

    if not is_stream:
        response = ChatCompletionResponse(
            # id, created is auto build from Field default_factory
            model=model_name,
            choices=[
                ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role= 'assistant', content=content), # LLM response
                    finish_reason="stop"
                )
            ],
            usage=UsageInfo(
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                total_tokens=total_tokens
            )
        )
        return response
    
    else:
        # Streaming response
        async def _stream_generator() -> AsyncGenerator[str, None]:
            request_id = f"chatcmpl-{uuid.uuid4().hex}"
            created_timestamp = int(time.time())

            # 1. init chunk (role)
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
            await asyncio.sleep(0.01) # wait for a short time

            # 2. content chunk (whole content)
            if content: # if content is not empty
                content_chunk = ChatCompletionStreamResponse(
                    id=request_id,
                    model=model_name,
                    created=int(time.time()),
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

            # 3. End chunk (finish reason)
            final_chunk = ChatCompletionStreamResponse(
                id=request_id,
                model=model_name,
                created=int(time.time()),
                choices=[
                    ChatCompletionStreamChoice(
                        index=0,
                        delta=DeltaMessage(), # empty delta
                        finish_reason="stop"
                    )
                ]
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"

            # 4. stream end message
            yield "data: [DONE]\n\n"

        # return the async generator
        return _stream_generator()