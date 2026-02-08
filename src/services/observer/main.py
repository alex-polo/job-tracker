import asyncio
import logging
from typing import TYPE_CHECKING

from .scheduler import ParseScheduler
from .tasks import hh_parse_task

if TYPE_CHECKING:
    from src.core.conf import ObserverSettings

log = logging.getLogger(__name__)


async def _main(settings: ObserverSettings) -> None:
    """Main function."""
    scheduler = ParseScheduler(settings=settings.scheduler)

    for source in settings.sources:
        log.debug(
            "Adding job for source: %s, url: %s",
            source.source_type,
            source.url,
        )

        scheduler.add_job(
            job_id=source.source_type,
            func=hh_parse_task,
            interval_minutes=source.period_minutes,
            task_args=(source.url,),
        )
        log.debug("Added job for source: %s", source.source_type)

    scheduler.start()

    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown()
        log.info("Observer stopped")


def run_observer(settings: ObserverSettings) -> None:
    """Run observer."""
    log.info("Start observer")
    asyncio.run(_main(settings=settings))
    log.info("Stop observer")
