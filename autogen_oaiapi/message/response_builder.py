from autogen_oaiapi.base.types import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice, UsageInfo

def build_openai_response(model_name, result, trminate_text = "", idx=None, source=None):
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