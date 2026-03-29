from src.services.base import ChatContext, ChatResult


class EchoChatService:
    def __init__(self, prefix: str = "echo: ") -> None:
        self.prefix = prefix

    async def reply(self, context: ChatContext) -> ChatResult:
        message = (context.message or "").strip()
        if not message:
            return ChatResult(text="메시지를 다시 보내주세요.")
        if self.prefix:
            return ChatResult(text=f"{self.prefix}{message}")
        return ChatResult(text=message)

