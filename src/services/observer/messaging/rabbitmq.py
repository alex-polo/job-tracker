import logging
from typing import TYPE_CHECKING

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractExchange
from pamqp.commands import Basic

from src.core.rabbitmq import (
    RabbitMQClient,
    RabbitMQInitializeError,
    RabbitMQPublishError,
    RabbitMQSerializationError,
    RabbitMQTimeoutError,
)

from .base import IMessageSender

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractExchange,
    )

    from src.core.conf import RabbitMQPublisherConfig, RabbitMQSettings
    from src.services.observer.entity import VacancyEntity


log = logging.getLogger(__name__)


class MQPublisher(IMessageSender, RabbitMQClient):
    """Publisher for sending vacancies to RabbitMQ."""

    def __init__(
        self,
        rabbitmq_settings: RabbitMQSettings,
        publisher_settings: RabbitMQPublisherConfig,
    ) -> None:
        """Initialize the MQPublisher."""
        super().__init__(
            url=rabbitmq_settings.url,
            connection_ttl=rabbitmq_settings.connection_ttl,
        )

        self.publisher_settings = publisher_settings
        self.exchanges_map: dict[str, AbstractExchange] = {}

        # self.exchange_name = "job_tracker"
        # self.queue_name = "vacancies"
        # self.routing_key = "vacancies"
        # self.queue_message_ttl = int(
        #     timedelta(minutes=10).total_seconds() * 1000
        # )
        # self.queue_ttl = int(timedelta(seconds=15).total_seconds())

        # self.dlx_exchange_name = "dlx_job_tracker"
        # self.dl_queue_name = "dl_vacancies"
        # self.dl_routing_key = "failed.vacancies"
        # self.dl_queue_message_ttl = int(
        #     timedelta(days=2).total_seconds() * 1000
        # )

    async def _initialize(self) -> None:
        """Initialize RabbitMQ infrastructure."""
        log.debug("Setting up RabbitMQ infrastructure...")

        if self.channel is None:
            log.error("Channel is not initialized")
            raise RabbitMQInitializeError("Channel is not initialized")

        for exchange_config in self.publisher_settings.topology.exchanges:
            self.exchanges_map[
                exchange_config.name
            ] = await self._declare_exchanges(
                channel=self.channel,
                exchange_name=exchange_config.name,
                exchange_type=exchange_config.type,
            )

        # self.dlx_exchange = await self._declare_direct_exchanges(
        #     channel=self.channel,
        #     exchange_name=self.dlx_exchange_name,
        # )

        # self.exchange = await self._declare_direct_exchanges(
        #     channel=self.channel,
        #     exchange_name=self.exchange_name,
        # )

        for queue_config in self.publisher_settings.topology.queues:
            await self._declare_queue(
                queue_name=queue_config.name,
                exchange_name=queue_config.exchange_name,
                routing_key=queue_config.routing_key,
                channel=self.channel,
                queue_timeout=queue_config.timeout,
                arguments=queue_config.arguments,
            )

        # await self._declare_queue(
        #     queue_name=self.dl_queue_name,
        #     exchange_name=self.dlx_exchange_name,
        #     routing_key=self.dl_routing_key,
        #     channel=self.channel,
        #     queue_timeout=self.queue_ttl,
        #     arguments={
        #         "x-message-ttl": self.dl_queue_message_ttl,
        #     },
        # )

        # await self._declare_queue(
        #     queue_name=self.queue_name,
        #     exchange_name=self.exchange_name,
        #     routing_key=self.routing_key,
        #     channel=self.channel,
        #     queue_timeout=self.queue_ttl,
        #     arguments={
        #         "x-message-ttl": self.queue_message_ttl,
        #         "x-dead-letter-exchange": self.dlx_exchange_name,
        #         "x-dead-letter-routing-key": self.dl_routing_key,
        #     },
        # )
        log.debug("RabbitMQ connection setup complete")

    async def publish_vacancy(self, vacancy: VacancyEntity) -> bool:
        """Send a message to RabbitMQ."""
        try:
            exchange: AbstractExchange = self.exchanges_map[
                self.publisher_settings.vacancy_exchange_name
            ]
            if exchange is None:
                raise RabbitMQInitializeError("Exchange is not initialized")

            log.debug("Publishing message: %s", vacancy)

            confirmation: (
                Basic.Ack | Basic.Nack | Basic.Reject | None
            ) = await exchange.publish(
                Message(
                    body=vacancy.to_json(),
                    delivery_mode=DeliveryMode.PERSISTENT,
                    message_id=vacancy.hash,
                ),
                routing_key=self.publisher_settings.vacancy_routing_key,
                mandatory=True,
            )

            if isinstance(confirmation, Basic.Ack):
                log.debug("Message acked: %s", vacancy)
                return True

            log.warning("Message nacked/rejected: %s", vacancy)
            return False

        except TimeoutError as e:
            log.error("Publish timeout: %s", e)
            raise RabbitMQTimeoutError(f"Publish timeout: {e}") from e

        except (ValueError, TypeError) as e:
            log.error("Failed to serialize vacancy: %s", e)
            raise RabbitMQSerializationError(
                f"Serialization error: {e}"
            ) from e

        except Exception as e:
            log.error("Failed to publish vacancy: %s", e)
            raise RabbitMQPublishError(f"Failed to publish: {e}") from e

    async def send_message(self, vacancy: VacancyEntity) -> bool:
        """Send a message to the message broker."""
        return await self.publish_vacancy(vacancy=vacancy)
