from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from src.core.conf.classes import RabbitMQSettings, SourceType
from src.core.database import DB_MANAGER
from src.services.observer.messaging.rabbitmq import MQPublisher

from .loaders.head_hunter_loader import HeadHunterLoader
from .repositories.vacancy import VacancyRepository
from .scheduler import ParseScheduler
from .tasks.polling_task import PollingTask

if TYPE_CHECKING:
    from src.core.conf import ObserverSettings
    from src.core.conf.mq_topology import RabbitMQPublisherConfig

    from .tasks import ISchedulerTask

log = logging.getLogger(__name__)


def make_polling_task(mq_publisher: MQPublisher) -> ISchedulerTask:
    """Create polling ISchedulerTask instance."""
    return PollingTask(
        loader=HeadHunterLoader(),
        repository=VacancyRepository(),
        mq_publisher=mq_publisher,
    )


async def main(
    settings: ObserverSettings,
    rabbitmq_settings: RabbitMQSettings,
    publisher_settings: RabbitMQPublisherConfig,
) -> None:
    """Main function."""
    async with MQPublisher(
        rabbitmq_settings=rabbitmq_settings,
        publisher_settings=publisher_settings,
    ) as mq_publisher:
        scheduler = ParseScheduler(settings=settings.scheduler)

        for source in settings.sources:
            log.debug(
                "Adding job for source: %s, url: %s",
                source.source_type,
                source.url,
            )
            if source.source_type == SourceType.HH:
                scheduler.add_job(
                    job_id=str(source.source_type),
                    func=make_polling_task(mq_publisher=mq_publisher).run,
                    interval_minutes=source.period_minutes,
                    task_args=(source.url,),
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
    settings: ObserverSettings,
    rabbitmq_settings: RabbitMQSettings,
    publisher_settings: RabbitMQPublisherConfig,
) -> None:
    """Run observer."""
    log.info("Start observer")
    asyncio.run(
        main(
            settings=settings,
            rabbitmq_settings=rabbitmq_settings,
            publisher_settings=publisher_settings,
        )
    )
    log.info("Stop observer")
