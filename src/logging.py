import logging
from logging.config import dictConfig


def configure_logging(level: str) -> None:
    root_logger = logging.getLogger()
    normalized_level = level.upper()

    if root_logger.handlers:
        root_logger.setLevel(normalized_level)
        return

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "level": normalized_level,
                "handlers": ["default"],
            },
            "loggers": {
                "httpx": {
                    "level": "WARNING",
                },
                "httpcore": {
                    "level": "WARNING",
                },
            },
        }
    )
