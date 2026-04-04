import asyncio
import logging
from typing import TYPE_CHECKING, Final

from src.core.conf import RabbitMQSettings, SourceType
from src.core.database import DB_MANAGER
from src.services.scrapper.ai_analyst.analyst import VacancyAIAnalyst
from src.services.scrapper.messaging.rabbitmq import MQPublisher
from src.services.scrapper.tasks.make import make_headhunter_polling_task

from .scheduler import ParseScheduler

if TYPE_CHECKING:
    from src.core.conf import ScrapperSettings
    from src.core.conf.classes import AIAnalystSettings
    from src.core.conf.mq_topology import RabbitMQPublisherConfig


log = logging.getLogger(__name__)

OFFSET_SECONDS: Final[int] = 5


def make_ai_analyst(conf: AIAnalystSettings) -> VacancyAIAnalyst:
    """Create AI Analyst instance."""
    return VacancyAIAnalyst(
        base_url=conf.base_url,
        api_key=conf.api_key,
        model=conf.model,
    )


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
    ai_analyst = make_ai_analyst(settings.ai_analyst)
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
                        mq_publisher=mq_publisher,
                        loader_settings=settings.httpx_settings,
                        ai_analyst=ai_analyst,
                        source_settings=source,
                    ).run,
                    interval_minutes=source.period_minutes,
                    stagger_first_run=True,
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
