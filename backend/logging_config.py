import logging
import os
from logging.config import dictConfig

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}

def configure_logging() -> None:
    # configure logging level
    configured_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if configured_level not in VALID_LOG_LEVELS:
        configured_level = "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": (
                        "%(asctime)s "
                        "%(levelname)s "
                        "[%(name)s] "
                        "%(message)s"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": configured_level,
                "handlers": ["console"],
            },
        }
    )

    logging.getLogger(__name__).info(
        "Logging configured with level %s",
        configured_level,
    )