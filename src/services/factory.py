from functools import lru_cache

from src.config import get_settings
from src.services.base import ChatService
from src.services.conversation_store import InMemoryConversationStore
from src.services.dify import DifyChatService


@lru_cache
def get_chat_service() -> ChatService:
    settings = get_settings()

    if not settings.dify_api_key:
        raise RuntimeError(
            "DIFY_API_KEY is required."
        )

    return DifyChatService(
        base_url=settings.dify_base_url,
        api_key=settings.dify_api_key,
        timeout_seconds=settings.dify_read_timeout_seconds,
        conversation_store=InMemoryConversationStore(),
    )
