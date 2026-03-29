from typing import Any

from pydantic import BaseModel, Field


class KakaoUser(BaseModel):
    id: str | None = None
    type: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class KakaoUserRequest(BaseModel):
    callbackUrl: str | None = None
    utterance: str = ""
    lang: str | None = None
    timezone: str | None = None
    user: KakaoUser | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    block: dict[str, Any] | None = None


class KakaoSkillRequest(BaseModel):
    userRequest: KakaoUserRequest = Field(default_factory=KakaoUserRequest)
    contexts: list[dict[str, Any]] = Field(default_factory=list)
    bot: dict[str, Any] | None = None
    action: dict[str, Any] | None = None

    @property
    def user_id(self) -> str | None:
        user = self.userRequest.user
        if not user or not user.id:
            return None
        return f"{user.type or 'user'}:{user.id}"


def build_simple_text_response(text: str) -> dict[str, Any]:
    message = (text or "").strip() or "빈 응답입니다."
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": message,
                    }
                }
            ]
        },
    }


def build_callback_ack_response(text: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "version": "2.0",
        "useCallback": True,
    }
    if text:
        payload["data"] = {"text": text}
    return payload

