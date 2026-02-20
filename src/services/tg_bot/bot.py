import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from .consumer import rabbit_consumer
from .handlers import register_commands

if TYPE_CHECKING:
    from src.core.conf.classes import RabbitMQSettings, TgBotConfig
    from src.core.conf.mq_topology import RabbitMQConsumerConfig


log = logging.getLogger(__name__)


DEFAULT_COMMANDS: list[BotCommand] = [
    BotCommand(command="start", description="Start the bot"),
]


def run_bot(
    tg_bot_config: TgBotConfig,
    rabbitmq_settings: RabbitMQSettings,
    consumer_config: RabbitMQConsumerConfig,
) -> None:
    """Run the Telegram bot and start the RabbitMQ consumer.

    Args:
        tg_bot_config: Telegram bot configuration including token and user IDs.
        rabbitmq_settings: RabbitMQ connection settings (URL, TTL).
        consumer_config: Consumer configuration including queue settings.
    """
    log.info("Starting bot...")
    asyncio.run(
        main(
            tg_bot_config=tg_bot_config,
            rabbitmq_settings=rabbitmq_settings,
            consumer_config=consumer_config,
        )
    )
    log.info("Bot stopped")


async def main(
    tg_bot_config: TgBotConfig,
    rabbitmq_settings: RabbitMQSettings,
    consumer_config: RabbitMQConsumerConfig,
) -> None:
    """Initialize and run all bot components.

    This async function performs the following steps:
    1. Creates Dispatcher and Bot instances
    2. Registers command handlers
    3. Sets bot commands for the Telegram menu
    4. Starts the RabbitMQ consumer task
    5. Starts polling for Telegram updates

    Args:
        tg_bot_config: Telegram bot configuration including token and user IDs.
        rabbitmq_settings: RabbitMQ connection settings (URL, TTL).
        consumer_config: Consumer configuration including queue settings.

    """
    log.info("Waiting 60s for RabbitMQ topology to be ready...")
    await asyncio.sleep(60)

    log.info("Initializing dispatcher and bot...")
    dp = Dispatcher()
    bot = Bot(token=tg_bot_config.token)
    log.info("Bot initialized for user_ids=%s", tg_bot_config.user_ids)

    log.info("Registering commands...")
    register_commands(dp)

    log.info(
        "Setting bot commands: %s", [cmd.command for cmd in DEFAULT_COMMANDS]
    )
    await bot.set_my_commands(DEFAULT_COMMANDS)

    log.info("Starting RabbitMQ consumer task...")
    consumer_task = asyncio.create_task(
        rabbit_consumer(
            bot=bot,
            rabbitmq_settings=rabbitmq_settings,
            consumer_config=consumer_config,
            user_ids=tg_bot_config.user_ids,
            send_timeout=10,
        )
    )

    try:
        log.info("Starting polling...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received")
    finally:
        log.info("Shutting down...")
        consumer_task.cancel()
        await consumer_task
        await bot.session.close()
        log.info("Bot session closed")
