from autogen_core.models import AssistantMessage
from autogen_oaiapi.base.types import ChatMessage, ChatCompletionResponse, ChatCompletionResponseChoice

def build_openai_response(result: AssistantMessage):
    return ChatCompletionResponse(
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=ChatMessage(role="assistant", content=result.content),
                finish_reason="stop"
            )
        ],
        usage={"prompt_tokens": 0, "completion_tokens": 0}
    )