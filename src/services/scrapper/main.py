import asyncio
import logging
from typing import TYPE_CHECKING, Final

from src.core.conf.classes import RabbitMQSettings, SourceType
from src.core.database import DB_MANAGER
from src.services.scrapper.messaging.rabbitmq import MQPublisher
from src.services.scrapper.tasks.make import make_headhunter_polling_task

from .scheduler import ParseScheduler

if TYPE_CHECKING:
    from src.core.conf import ScrapperSettings
    from src.core.conf.mq_topology import RabbitMQPublisherConfig


log = logging.getLogger(__name__)

OFFSET_SECONDS: Final[int] = 5


async def main(
    settings: ScrapperSettings,
    rabbitmq_settings: RabbitMQSettings,
    publisher_settings: RabbitMQPublisherConfig,
) -> None:
    """Run the main observer loop.

    Initializes the RabbitMQ publisher, configures the scheduler
    with jobs for each source, and starts polling. Gracefully
    shuts down on interruption.

    Args:
        settings: Observer configuration settings.
        rabbitmq_settings: RabbitMQ connection settings.
        publisher_settings: RabbitMQ publisher topology configuration.
    """
    async with MQPublisher(
        rabbitmq_settings=rabbitmq_settings,
        publisher_settings=publisher_settings,
    ) as mq_publisher:
        scheduler = ParseScheduler(settings=settings.scheduler)

        for idx, source in enumerate(settings.sources):
            log.debug(
                "Adding job for source: %s, url: %s",
                source.source_type,
                source.url,
            )
            if source.source_type == SourceType.HH:
                scheduler.add_job(
                    job_id=f"{source.source_type.value}_{source.url}",
                    func=make_headhunter_polling_task(
                        main_tag=source.tag,
                        url=source.url,
                        keywords=source.keywords,
                        mq_publisher=mq_publisher,
                        loader_settings=settings.httpx_settings,
                    ).run,
                    interval_minutes=source.period_minutes,
                    # task_args=(source.url,),  # noqa: ERA001
                    stagger_first_run=True,  # Распределяем первый запуск
                    offset_seconds=idx * OFFSET_SECONDS,
                )
                log.debug("Added job for source: %s", source.source_type)

        scheduler.start()

        try:
            await asyncio.Event().wait()
        finally:
            log.info("Shutting down scheduler")
            scheduler.shutdown()
            log.info("Disposing database engine")
            await DB_MANAGER.dispose_engine()
            log.info("Exiting")
            log.info("Observer stopped")


def run_observer(
    settings: ScrapperSettings,
    rabbitmq_settings: RabbitMQSettings,
    publisher_settings: RabbitMQPublisherConfig,
) -> None:
    """Entry point for running the screpper.

    Initializes and runs the scrapper service using asyncio.

    Args:
        settings: Observer configuration settings.
        rabbitmq_settings: RabbitMQ connection settings.
        publisher_settings: RabbitMQ publisher topology configuration.
    """
    log.info("Start scrapper ...")
    asyncio.run(
        main(
            settings=settings,
            rabbitmq_settings=rabbitmq_settings,
            publisher_settings=publisher_settings,
        )
    )
    log.info("Stop observer")
