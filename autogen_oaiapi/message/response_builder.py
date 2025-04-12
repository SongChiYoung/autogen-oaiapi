from autogen_oaiapi.base.types import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice

def build_openai_response(result, idx=None, source=None):
    if idx is None and source is None:
        idx = 0
    if idx is not None and source is not None:
        raise ValueError("Either idx or source must be provided, not both.")
    
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

    if idx is not None:
        result_message = result.messages[-idx]

    return ChatCompletionResponse(
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=ChatMessage(role="assistant", content=result_message.content),
                finish_reason="stop"
            )
        ],
        usage={"prompt_tokens": total_prompt_tokens, "completion_tokens": total_completion_tokens}
    )