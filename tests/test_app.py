from fastapi.testclient import TestClient

from api.index import app
from src.config import get_settings
from src.services.base import ChatResult
from src.services.dify import DifyChatService
from src.services.factory import get_chat_service


def reset_settings() -> None:
    get_settings.cache_clear()
    get_chat_service.cache_clear()


def test_health_returns_ok(monkeypatch) -> None:
    monkeypatch.setenv("DIFY_API_KEY", "test-key")
    reset_settings()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["backend"] == "dify"


def test_webhook_returns_sync_response_without_callback(monkeypatch) -> None:
    monkeypatch.setenv("DIFY_API_KEY", "test-key")
    reset_settings()

    async def fake_reply(self, context):  # type: ignore[no-untyped-def]
        return ChatResult(text="디파이 응답")

    monkeypatch.setattr(DifyChatService, "reply", fake_reply)
    client = TestClient(app)

    response = client.post(
        "/kakao/webhook",
        json={
            "userRequest": {
                "utterance": "안녕",
                "user": {
                    "id": "demo-user",
                    "type": "botUserKey",
                },
            }
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "디파이 응답",
                    }
                }
            ]
        },
    }


def test_webhook_returns_callback_ack_and_posts_callback(monkeypatch) -> None:
    monkeypatch.setenv("DIFY_API_KEY", "test-key")
    reset_settings()
    sent_payloads: list[tuple[str, dict]] = []

    async def fake_reply(self, context):  # type: ignore[no-untyped-def]
        return ChatResult(text="콜백 디파이 응답")

    async def fake_send_callback_payload(callback_url: str, payload: dict) -> None:
        sent_payloads.append((callback_url, payload))

    monkeypatch.setattr(DifyChatService, "reply", fake_reply)
    monkeypatch.setattr(
        "src.services.callback.send_callback_payload",
        fake_send_callback_payload,
    )

    client = TestClient(app)
    response = client.post(
        "/kakao/webhook",
        json={
            "userRequest": {
                "callbackUrl": "https://callback.example.com/token",
                "utterance": "콜백 테스트",
                "user": {
                    "id": "demo-user",
                    "type": "botUserKey",
                },
            }
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "version": "2.0",
        "useCallback": True,
        "data": {
            "text": "질문을 보고 고민하는 중입니다."
        },
    }
    assert sent_payloads == [
        (
            "https://callback.example.com/token",
            {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "콜백 디파이 응답",
                            }
                        }
                    ]
                },
            },
        )
    ]
