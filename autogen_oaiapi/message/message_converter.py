from typing import List
from autogen_agentchat.messages import (
    TextMessage,
    ChatMessage,
)
from autogen_oaiapi.base.types import ChatCompletionMessage  # ToDo: Change name

def convert_to_llm_messages(messages: List[ChatCompletionMessage]) -> List[ChatMessage]:
    """
    Convert a list of ChatMessage objects to LLM-compatible TextMessage objects.

    Args:
        messages (list[ChatMessage]): List of chat messages with roles and content.

    Returns:
        list[TextMessage]: List of converted TextMessage objects for LLM processing.
    """
    converted: List[ChatMessage] = []
    for m in messages:
        if m.content:
            converted.append(TextMessage(content=m.content, source=m.role))
    return converted