class InMemoryConversationStore:
    def __init__(self) -> None:
        self._conversation_ids: dict[str, str] = {}

    def get(self, user_id: str | None) -> str | None:
        if not user_id:
            return None
        return self._conversation_ids.get(user_id)

    def set(self, user_id: str | None, conversation_id: str | None) -> None:
        if not user_id or not conversation_id:
            return
        self._conversation_ids[user_id] = conversation_id

