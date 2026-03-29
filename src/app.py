import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import BackgroundTasks, FastAPI, Header, Request
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.logging import configure_logging
from src.models import (
    KakaoSkillRequest,
    build_callback_ack_response,
    build_simple_text_response,
)
from src.services.callback import build_reply_text, process_callback_request

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.last_debug_callback = None
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, Any]:
    runtime_settings = get_settings()
    return {
        "ok": True,
        "name": runtime_settings.app_name,
        "version": runtime_settings.app_version,
        "backend": runtime_settings.backend,
        "message": "vercel fastapi adapter is running",
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    runtime_settings = get_settings()
    return {
        "ok": True,
        "env": runtime_settings.app_env,
        "backend": runtime_settings.backend,
    }


@app.post("/kakao/webhook")
async def kakao_webhook(
    payload: KakaoSkillRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
    kakao_instance: str | None = Header(default=None, alias="KakaoI-Instance"),
) -> JSONResponse:
    runtime_settings = get_settings()
    callback_url = payload.userRequest.callbackUrl

    logger.info(
        "Received Kakao webhook request_id=%s user_id=%s callback=%s",
        x_request_id,
        payload.user_id or (request.client.host if request.client else "anonymous"),
        bool(callback_url),
    )

    if callback_url:
        background_tasks.add_task(
            process_callback_request,
            payload.model_dump(mode="python"),
            x_request_id,
            kakao_instance,
        )
        return JSONResponse(
            content=build_callback_ack_response(
                runtime_settings.kakao_callback_pending_text
            ),
            status_code=200,
        )

    try:
        text = await build_reply_text(payload, x_request_id, kakao_instance)
    except Exception:
        logger.exception(
            "Failed to process synchronous Kakao webhook request_id=%s user_id=%s",
            x_request_id,
            payload.user_id,
        )
        text = runtime_settings.kakao_callback_error_text

    return JSONResponse(
        content=build_simple_text_response(text),
        status_code=200,
    )


if settings.app_env != "production":

    @app.post("/debug/callback-sink")
    async def debug_callback_sink(payload: dict[str, Any]) -> dict[str, Any]:
        app.state.last_debug_callback = payload
        return {"ok": True}


    @app.get("/debug/callback-sink")
    async def debug_callback_sink_read() -> dict[str, Any]:
        return {"last_callback": app.state.last_debug_callback}
