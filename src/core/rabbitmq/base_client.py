import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

import aio_pika
from aio_pika import ExchangeType
from aio_pika.abc import AbstractExchange, AbstractQueue

from src.core.rabbitmq.exceptions import (
    RabbitMQConnectionError,
    RabbitMQInitializeError,
    RabbitMQTimeoutError,
)

if TYPE_CHECKING:
    from aio_pika.abc import (
        AbstractChannel,
        AbstractExchange,
        AbstractQueue,
        AbstractRobustConnection,
    )
    from pamqp.common import FieldValue


log = logging.getLogger(__name__)


class RabbitMQClient(ABC):
    """Manages the connection to RabbitMQ."""

    def __init__(
        self,
        url: str,
        connection_ttl: int = 60,
        publisher_confirms: bool = True,
    ) -> None:
        """Initialize the RabbitMQClient."""
        self.publisher_confirms = publisher_confirms
        self.url: str = url
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self.dlx_exchange: AbstractExchange | None = None
        self.exchange: AbstractExchange | None = None
        self.connection_ttl = connection_ttl

    @abstractmethod
    async def _initialize(self) -> None:
        """Initialize the RabbitMQClient."""

    async def _declare_exchanges(
        self,
        channel: AbstractChannel,
        exchange_name: str,
        exchange_type: ExchangeType,
    ) -> AbstractExchange:
        """Declare exchanges."""
        log.debug("Declaring exchange: %s", exchange_name)
        try:
            exchange: AbstractExchange = await channel.declare_exchange(
                exchange_name,
                exchange_type,
                durable=True,
            )
            log.debug("Exchange declared: %s", exchange_name)
            return exchange

        except TimeoutError as e:
            log.error("Exchange declaration timeout: %s", e)
            raise RabbitMQTimeoutError(
                f"Exchange declaration timeout: {e}"
            ) from e

        except Exception as e:
            log.error("Failed to declare exchange %s: %s", exchange_name, e)
            raise RabbitMQInitializeError(
                f"Failed to declare exchange: {e}"
            ) from e

    async def _declare_queue(
        self,
        queue_name: str,
        channel: AbstractChannel,
        exchange_name: str,
        routing_key: str,
        queue_timeout: int,
        arguments: dict[str, FieldValue],
    ) -> None:
        """Declare queues."""
        log.debug(
            "Declaring queue: %s (timeout=%ss)",
            queue_name,
            queue_timeout,
        )
        try:
            queue: AbstractQueue = await channel.declare_queue(
                queue_name,
                durable=True,
                arguments=arguments,
                timeout=queue_timeout,
            )
            await queue.bind(
                exchange_name,
                routing_key=routing_key,
            )
            log.debug(
                "Queue declared: %s",
                queue_name,
            )

        except TimeoutError as e:
            log.error("Queue declaration timeout: %s", e)
            raise RabbitMQTimeoutError(
                f"Queue declaration timeout: {e}"
            ) from e

        except Exception as e:
            log.error("Failed to declare queue %s: %s", queue_name, e)
            raise RabbitMQInitializeError(
                f"Failed to declare queue: {e}"
            ) from e

    async def _create_connection(self) -> None:
        """Create connection and channel to RabbitMQ."""
        try:
            log.debug("Connecting to RabbitMQ...")
            self.connection = await aio_pika.connect_robust(
                url=self.url,
                timeout=self.connection_ttl,
            )
            log.debug("Connected to RabbitMQ")

            log.debug("Opening channel...")
            self.channel = await self.connection.channel(  # type: ignore
                publisher_confirms=self.publisher_confirms,
            )
            log.debug("Channel opened")

        except TimeoutError as e:
            log.error("Connection timeout: %s", e)
            raise RabbitMQTimeoutError(f"Connection timeout: {e}") from e

        except Exception as e:
            log.error("Failed to connect to RabbitMQ: %s", e)
            raise RabbitMQConnectionError(f"Failed to connect: {e}") from e

        try:
            await self._initialize()

        except RabbitMQInitializeError:
            raise

        except Exception as e:
            log.error("Failed to initialize infrastructure: %s", e)
            raise RabbitMQInitializeError(f"Failed to initialize: {e}") from e

    async def close(self) -> None:
        """Close the connection."""
        log.debug("Closing RabbitMQ connection...")
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
            log.debug("Channel closed")

        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            log.debug("Connection closed")

    async def __aenter__(self) -> Self:
        """Enter the context manager."""
        await self._create_connection()
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit the context manager."""
        await self.close()
