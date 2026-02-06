from logging.config import dictConfig
from typing import Any

from .instance import APP_SETTINGS


def setup_logging() -> None:
    """Setup logging."""
    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": APP_SETTINGS.logging.log_format,
                "datefmt": APP_SETTINGS.logging.log_date_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "log_file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": APP_SETTINGS.logging.directory
                / APP_SETTINGS.logging.log_file,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {
                "handlers": ["log_file", "console"],
                "level": APP_SETTINGS.logging.log_level,
                "propagate": False,
            },
        },
    }

    if not APP_SETTINGS.logging.directory.exists():
        APP_SETTINGS.logging.directory.mkdir(parents=True, exist_ok=True)

    dictConfig(log_config)
