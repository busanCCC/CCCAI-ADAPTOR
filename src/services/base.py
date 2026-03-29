from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class ChatContext:
    message: str
    user_id: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ChatResult:
    text: str
    raw: dict[str, Any] | None = None
    conversation_id: str | None = None


class ChatService(Protocol):
    async def reply(self, context: ChatContext) -> ChatResult:
        """Return a chatbot response for the incoming message."""

