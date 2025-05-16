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
        messages (list[ChatCompletionMessage]): List of chat messages with roles and content.

    Returns:
        list[ChatMessage]: List of converted ChatMessage objects for LLM processing.
    """
    converted: List[ChatMessage] = []
    for m in messages:
        if not m.content:
            continue
        if isinstance(m.content, list):
            for c in m.content:
                converted.append(TextMessage(content=c.text, source=m.role))
        elif isinstance(m.content, str):
            converted.append(TextMessage(content=m.content, source=m.role))
    return converted