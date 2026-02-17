from typing import ClassVar

from aio_pika import ExchangeType

from .classes import ExcangeConfig, QueueConfig

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
    message_ttl=600_000,
    durable=True,
    arguments={
        "x-message-ttl": 600_000,
        "x-dead-letter-exchange": "dlx_job_tracker",
        "x-dead-letter-routing-key": "failed.vacancies",
    },
    timeout=15,
)
dl_queue_config = QueueConfig(
    name="dl_vacancies",
    exchange_name="dlx_job_tracker",
    routing_key="failed.vacancies",
    message_ttl=172_800_000,
    durable=True,
    arguments={
        "x-message-ttl": 172_800_000,
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

    vacancy_exchange_name: str = "job_tracker"
    vacancy_routing_key: str = "vacancies"


__all__ = (
    "RabbitMQConsumerConfig",
    "RabbitMQPublisherConfig",
    "RabbitMQTopology",
)
