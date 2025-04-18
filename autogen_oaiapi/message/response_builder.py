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

def clean_message(content, removers):
    for remover in removers:
        content = content.replace(remover, "")
    content = (
                content
                .replace("TERMINATE", "") # default terminate text
                .replace("<think>", "") # default think text
                .replace("</think>", "") # default think text
    )
    return content
        

def build_content_chunk(request_id, model_name, content, finish_reason=None):
    content_chunk = ChatCompletionStreamResponse(
        id=request_id,
        model=model_name,
        created=int(time.time()),
        choices=[
            ChatCompletionStreamChoice(
                index=0,
                delta=DeltaMessage(content=content+"\n"),
                finish_reason=finish_reason
            )
        ]
    )
    return content_chunk



async def build_openai_response(model_name, result, terminate_texts = [], idx=None, source=None, is_stream=False, previous_messages=0):
    if idx is None and source is None:
        idx = 0
    if idx is not None and source is not None:
        raise ValueError("Either idx or source must be provided, not both.")
    if model_name is None:
        model_name = "autogen"

    def return_last_message(result):
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

        content = clean_message(content, terminate_texts)

        return content, total_prompt_tokens, total_completion_tokens, total_tokens

    if not is_stream:
        # Non-streaming response
        content, total_prompt_tokens, total_completion_tokens, total_tokens = return_last_message(result)
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
            # await asyncio.sleep(0.01) # wait for a short time

            content_chunk = build_content_chunk(request_id, model_name, "<think>")
            yield f"data: {content_chunk.model_dump_json()}\n\n"

            message_count = 0
            # 2. content chunk (streaming)
            async for message in result:
                if previous_messages > message_count:
                    message_count += 1
                    continue
                # print(f"message: {message}")
                # print(f"message.type: {type(message)}")
                if hasattr(message, "content") and message.content:
                    content_chunk = build_content_chunk(request_id, model_name, message.content)
                    yield f"data: {content_chunk.model_dump_json()}\n\n"
            else:
                content_chunk = build_content_chunk(request_id, model_name, "</think>")
                yield f"data: {content_chunk.model_dump_json()}\n\n"

                content, total_prompt_tokens, total_completion_tokens, total_tokens = return_last_message(message)
                content_chunk = build_content_chunk(request_id, model_name, content)
                yield f"data: {content_chunk.model_dump_json()}\n\n"

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
