from autogen_core.models import UserMessage, AssistantMessage, SystemMessage
from autogen_agentchat.messages import (
    TextMessage
)
from autogen_oaiapi.base.types import ChatMessage

def convert_to_llm_messages(messages: list[ChatMessage]):
    """
    Convert a list of ChatMessage objects to LLM-compatible TextMessage objects.

    Args:
        messages (list[ChatMessage]): List of chat messages with roles and content.

    Returns:
        list[TextMessage]: List of converted TextMessage objects for LLM processing.
    """
    converted = []
    for m in messages:
        if m.role == "user":
            converted.append(TextMessage(content=m.content, source="user"))
        elif m.role == "assistant":
            converted.append(TextMessage(content=m.content, source="assistant"))
        elif m.role == "system":
            converted.append(TextMessage(content=m.content, source="system"))
    return converted