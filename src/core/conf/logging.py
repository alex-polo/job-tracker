from logging.config import dictConfig
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .classes import LoggingSettings


def setup_logging(settings: LoggingSettings) -> None:
    """Setup logging."""
    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": settings.log_date_format,
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
                "filename": settings.directory / settings.log_file,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {
                "handlers": ["log_file", "console"],
                "level": settings.log_level,
                "propagate": False,
            },
        },
    }

    if not settings.directory.exists():
        settings.directory.mkdir(parents=True, exist_ok=True)

    dictConfig(log_config)
