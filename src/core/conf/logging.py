import logging
from typing import TYPE_CHECKING

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

if TYPE_CHECKING:
    from .classes import LoggingSettings


def setup_logging(settings: LoggingSettings) -> None:
    """Setup logging."""
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=str(settings.sentry_dsn),
            environment=settings.sentry_environment,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            enable_tracing=True,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=getattr(logging, settings.sentry_log_level),
                ),
            ],
        )

    logging.basicConfig(
        level=settings.log_level,
        format=settings.log_format,
        datefmt=settings.log_date_format,
        force=True,
    )

    for logger in logging.Logger.manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            logger.setLevel(settings.log_level)
            logger.propagate = True
