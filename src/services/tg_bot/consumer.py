import asyncio
import logging
from typing import TYPE_CHECKING

from aiogram.enums import ParseMode

from src.core.rabbitmq import RabbitMQClient
from src.core.rabbitmq.exceptions import RabbitMQConnectionError

from .entity import RecivedVacancyEntity

if TYPE_CHECKING:
    from aio_pika.abc import AbstractQueue
    from aiogram import Bot

    from src.core.conf import RabbitMQConsumerConfig, RabbitMQSettings


log = logging.getLogger(__name__)


class RabbitMQConsumer(RabbitMQClient):
    """Manages the RabbitMQ connection for consuming vacancy messages.

    This class extends RabbitMQClient and provides a consumer-specific
    implementation for connecting to RabbitMQ and processing messages
    from the vacancy queue.

    Attributes:
        url: RabbitMQ connection URL.
        connection_ttl: Connection time-to-live in seconds.
    """

    def __init__(self, url: str, connection_ttl: int = 60) -> None:
        """Initialize the RabbitMQConsumer.

        Args:
            url: RabbitMQ connection URL (e.g., "amqp://guest:guest@localhost/").
            connection_ttl: Connection time-to-live in seconds. Defaults to 60.
        """
        super().__init__(url=url, connection_ttl=connection_ttl)

    async def _initialize(self) -> None:
        """Initialize RabbitMQ infrastructure."""
        pass


async def rabbit_consumer(
    bot: Bot,
    rabbitmq_settings: RabbitMQSettings,
    consumer_config: RabbitMQConsumerConfig,
    user_ids: list[int],
    send_timeout: int = 10,
) -> None:
    """Consume vacancy messages from RabbitMQ and send them to Telegram users.

    This function establishes a connection to RabbitMQ and declares
    the vacancy queue, and continuously consumes messages.
    Each message is parsed into a RecivedVacancyEntity and sent to
    all configured Telegram users.


    Args:
        bot: Configured aiogram Bot instance for sending messages.
        rabbitmq_settings: RabbitMQ connection settings (URL, TTL).
        consumer_config: Consumer configuration including queue settings.
        user_ids: List of Telegram user IDs to send vacancy messages to.
        send_timeout: Timeout in seconds for each send_message call.
    """
    log.info("Starting RabbitMQ consumer")
    try:
        async with RabbitMQConsumer(
            url=rabbitmq_settings.url,
            connection_ttl=rabbitmq_settings.connection_ttl,
        ) as consumer:
            if not consumer.channel:
                raise RabbitMQConnectionError("Channel not initialized")

            log.debug(
                "Declaring queue: %s", consumer_config.vacancy_queue.name
            )
            queue: AbstractQueue = await consumer._declare_queue(
                queue_name=consumer_config.vacancy_queue.name,
                exchange_name=consumer_config.vacancy_queue.exchange_name,
                routing_key=consumer_config.vacancy_queue.routing_key,
                channel=consumer.channel,
                queue_timeout=consumer_config.vacancy_queue.timeout,
                arguments=consumer_config.vacancy_queue.arguments,
            )

            log.info("Started consuming messages from queue: %s", queue.name)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    log.debug("Received message from queue: %s", queue.name)
                    recived_vacancy_entity = RecivedVacancyEntity.from_json(
                        json_bytes=message.body,
                    )

                    try:
                        for user_id in user_ids:
                            log.debug(
                                "Sending vacancy to user_id=%s: %s",
                                user_id,
                                recived_vacancy_entity,
                            )
                            await asyncio.wait_for(
                                bot.send_message(
                                    chat_id=user_id,
                                    text=recived_vacancy_entity.format_message(),
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=recived_vacancy_entity.create_keyboard(),
                                ),
                                timeout=send_timeout,
                            )

                        await message.ack()
                        log.debug("Successfully sent message to users")
                    except asyncio.CancelledError:
                        log.info("Consumer task cancelled")
                        await message.nack(requeue=True)
                        raise
                    except TimeoutError:
                        await message.reject()
                        log.error("Timeout while sending vacancy message")
                    except Exception as exc:
                        await message.reject()
                        log.error("Failed to send vacancy message: %s", exc)

    finally:
        log.info("RabbitMQ consumer stopped")


__all__ = ("RabbitMQConsumer", "rabbit_consumer")
