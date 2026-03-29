from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "kakao-dify-vercel-adapter"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    backend: Literal["echo", "dify"] = "echo"
    echo_prefix: str = "echo: "

    kakao_callback_pending_text: str = (
        "질문을 처리하고 있어요. 잠시만 기다려주세요."
    )
    kakao_callback_error_text: str = (
        "답변을 가져오는 중 문제가 생겼어요. 잠시 후 다시 시도해 주세요."
    )

    dify_base_url: str | None = None
    dify_api_key: str | None = None
    dify_read_timeout_seconds: float = 25.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

