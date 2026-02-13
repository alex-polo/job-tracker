import asyncio
import logging
from typing import TYPE_CHECKING

from src.core.conf.classes import SourceType
from src.core.database import DB_MANAGER

from .loaders.head_hunter_loader import HeadHunterLoader
from .repositories.vacancy import VacancyRepository
from .scheduler import ParseScheduler
from .tasks.polling_task import PollingTask

if TYPE_CHECKING:
    from src.core.conf import ObserverSettings

    from .tasks import ISchedulerTask

log = logging.getLogger(__name__)


def make_polling_task() -> ISchedulerTask:
    """Create polling ISchedulerTask instance."""
    return PollingTask(
        loader=HeadHunterLoader(),
        repository=VacancyRepository(),
    )


async def main(settings: ObserverSettings) -> None:
    """Main function."""
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
                func=make_polling_task().run,
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


def run_observer(settings: ObserverSettings) -> None:
    """Run observer."""
    log.info("Start observer")
    asyncio.run(main(settings=settings))
    log.info("Stop observer")
