"""Entry point for the Telegram bot service.

This module initializes and runs the Telegram bot, which receives notifications
from RabbitMQ and forwards them to users.
"""

import asyncio
import logging

from src.core.conf import TgBotSettings, setup_logging
from src.core.conf.classes import RabbitMQSettings
from src.core.conf.mq_topology import RabbitMQConsumerConfig
from src.services.tg_bot import run_bot

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    """Initialize and run the Telegram bot service.

    Exceptions:
        KeyboardInterrupt: Shuts down the service when interrupted by user.
        Exception: Logs any unexpected exceptions with full stack trace.
    """
    try:
        log = logging.getLogger(__name__)
        tg_bot_settings = TgBotSettings()  # type: ignore
        rabbitmq_settings = RabbitMQSettings()  # type: ignore
        consumer_config = RabbitMQConsumerConfig()
        setup_logging(settings=tg_bot_settings.logging)

        run_bot(
            tg_bot_config=tg_bot_settings.tg_bot,
            rabbitmq_settings=rabbitmq_settings,
            consumer_config=consumer_config,
        )
    except asyncio.exceptions.CancelledError:
        log.info("Cancelled by user")
    except Exception as e:
        log.exception(e)


if __name__ == "__main__":
    main()
