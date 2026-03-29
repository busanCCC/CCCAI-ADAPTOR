import httpx

from src.services.base import ChatContext, ChatResult
from src.services.conversation_store import InMemoryConversationStore


class DifyChatService:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_seconds: float,
        conversation_store: InMemoryConversationStore,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.conversation_store = conversation_store

    async def reply(self, context: ChatContext) -> ChatResult:
        payload: dict[str, object] = {
            "inputs": {},
            "query": context.message,
            "response_mode": "blocking",
            "user": context.user_id or "anonymous",
        }

        conversation_id = self.conversation_store.get(context.user_id)
        if conversation_id:
            payload["conversation_id"] = conversation_id

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_seconds)
        ) as client:
            response = await client.post(
                f"{self.base_url}/chat-messages",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

        data = response.json()
        next_conversation_id = data.get("conversation_id")
        self.conversation_store.set(context.user_id, next_conversation_id)

        answer = (data.get("answer") or "").strip()
        return ChatResult(
            text=answer or "Dify가 빈 응답을 반환했습니다.",
            raw=data,
            conversation_id=next_conversation_id,
        )

