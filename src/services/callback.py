import logging
from typing import Any

import httpx

from src.config import get_settings
from src.models import KakaoSkillRequest, build_simple_text_response
from src.services.base import ChatContext
from src.services.factory import get_chat_service

logger = logging.getLogger(__name__)


async def send_callback_payload(callback_url: str, payload: dict[str, Any]) -> None:
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        response = await client.post(callback_url, json=payload)
        response.raise_for_status()


async def build_reply_text(
    payload: KakaoSkillRequest,
    request_id: str | None = None,
    kakao_instance: str | None = None,
) -> str:
    service = get_chat_service()
    result = await service.reply(
        ChatContext(
            message=payload.userRequest.utterance or "",
            user_id=payload.user_id,
            meta={
                "request_id": request_id,
                "kakao_instance": kakao_instance,
                "timezone": payload.userRequest.timezone,
                "lang": payload.userRequest.lang,
            },
        )
    )
    return result.text


async def process_callback_request(
    payload_data: dict[str, Any],
    request_id: str | None = None,
    kakao_instance: str | None = None,
) -> None:
    settings = get_settings()
    payload = KakaoSkillRequest.model_validate(payload_data)
    callback_url = payload.userRequest.callbackUrl

    if not callback_url:
        logger.warning("Callback task skipped because callbackUrl is missing")
        return

    try:
        text = await build_reply_text(payload, request_id, kakao_instance)
        response_payload = build_simple_text_response(text)
    except Exception:
        logger.exception(
            "Failed to build callback response request_id=%s user_id=%s",
            request_id,
            payload.user_id,
        )
        response_payload = build_simple_text_response(
            settings.kakao_callback_error_text
        )

    try:
        await send_callback_payload(callback_url, response_payload)
    except Exception:
        logger.exception(
            "Failed to deliver callback request_id=%s user_id=%s callback_url=%s",
            request_id,
            payload.user_id,
            callback_url,
        )
