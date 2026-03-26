from typing import ClassVar, Final

from aio_pika import ExchangeType

from .classes import ExcangeConfig, QueueConfig

DLX_MESSGAE_TTL: Final[int] = 7 * 24 * 60 * 60 * 1000  # 7 days
MESSAGE_TTL: Final[int] = 60 * 60 * 1000  # 1 hour

dlx_exchange_config = ExcangeConfig(
    name="dlx_job_tracker",
    type=ExchangeType.DIRECT,
    durable=True,
)
exchange_config = ExcangeConfig(
    name="job_tracker",
    type=ExchangeType.DIRECT,
    durable=True,
)

queue_config = QueueConfig(
    name="vacancies",
    exchange_name="job_tracker",
    routing_key="vacancies",
    message_ttl=MESSAGE_TTL,
    durable=True,
    arguments={
        "x-message-ttl": MESSAGE_TTL,
        "x-dead-letter-exchange": "dlx_job_tracker",
        "x-dead-letter-routing-key": "failed.vacancies",
    },
    timeout=15,
)
dl_queue_config = QueueConfig(
    name="dl_vacancies",
    exchange_name="dlx_job_tracker",
    routing_key="failed.vacancies",
    message_ttl=DLX_MESSGAE_TTL,
    durable=True,
    arguments={
        "x-message-ttl": DLX_MESSGAE_TTL,
    },
    timeout=15,
)


class RabbitMQTopology:
    """Publisher topology."""

    exchanges: ClassVar[tuple[ExcangeConfig, ...]] = (
        dlx_exchange_config,
        exchange_config,
    )
    queues: ClassVar[tuple[QueueConfig, ...]] = (
        queue_config,
        dl_queue_config,
    )


class RabbitMQPublisherConfig:
    """Publisher config."""

    vacancy_exchange_name: str = "job_tracker"
    vacancy_routing_key: str = "vacancies"

    topology: RabbitMQTopology = RabbitMQTopology()


class RabbitMQConsumerConfig:
    """Consumer config."""

    perf_counter = ""

    vacancy_queue: QueueConfig = queue_config


__all__ = (
    "RabbitMQConsumerConfig",
    "RabbitMQPublisherConfig",
    "RabbitMQTopology",
)
