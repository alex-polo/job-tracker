import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from apscheduler import events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

if TYPE_CHECKING:
    from collections.abc import Callable

    from apscheduler.events import JobExecutionEvent

    from src.core.conf.classes import ScrapperSchedulerSettings


log = logging.getLogger(__name__)


class ParseScheduler:
    """Async scheduler for periodic parsing tasks.

    Wraps APScheduler's AsyncIOScheduler with simplified API
    for parsing workflows. On startup (next_run_time=datetime.now()).

    Example:
        scheduler = ParseScheduler(settings)
        scheduler.add_job(
            job_id="hh_parser",
            func=parse_hh,
            interval_minutes=5,
            task_args=(URL(str),),
        )
        scheduler.start()
    """

    def __init__(self, settings: ScrapperSchedulerSettings) -> None:
        """Initialize scheduler with timezone configuration.

        Args:
            settings: Scheduler configuration.
        """
        log.debug("Init scheduler")
        log.debug("Timezone: %s", settings.time_zone)

        self.scheduler = AsyncIOScheduler(timezone=settings.time_zone)
        self.scheduler.add_listener(
            self._job_error_listener,
            events.EVENT_JOB_ERROR,
        )

    def _job_error_listener(self, event: JobExecutionEvent) -> None:
        """Log errors from failed jobs.

        Called automatically by APScheduler on job failure.
        Does not suppress exceptions — only provides logging.

        Args:
            event: APScheduler event containing job_id and exc details.
        """
        if event.exception:
            log.error(f"Error in task: {event.job_id}: {event.exception}")

    def add_job(
        self,
        job_id: str,
        func: Callable[..., object],
        interval_minutes: int,
        task_args: tuple[object, ...] | None = None,
        stagger_first_run: bool = True,
        offset_seconds: int = 0,
    ) -> None:
        """Schedule a periodic task with configurable first run time.

        First run: `datetime.now() + offset_seconds`.
        Subsequent runs: every `interval_minutes`.
        Duplicate job_ids are replaced (replace_existing=True).

        Behavior:
            - max_instances=1: concurrent runs are blocked;.
            - coalesce=True: missed runs (misfire) are merged into one
              execution.
            - misfire_grace_time=60s: missed runs older than 60s.

        Args:
            job_id: Unique identifier for the job (must be string).
            func: Async or sync callable to execute periodically.
            interval_minutes: Interval between executions in minutes.
            task_args: Positional arguments passed to func on each run.
            stagger_first_run: If True, adds random delay)
            offset_seconds: Additional fixed delay in seconds.
                Useful for staggering multiple jobs of the same type.
        """
        self.scheduler.add_job(
            id=job_id,
            func=func,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=task_args,
            replace_existing=True,
            misfire_grace_time=60,
            coalesce=True,
            max_instances=1,
            stagger_first_run=stagger_first_run,
            next_run_time=datetime.now(tz=UTC)
            + timedelta(seconds=offset_seconds),
        )
        log.info(f"Add task '{job_id}': every {interval_minutes} minutes")

    def start(self) -> None:
        """Start the scheduler.

        Jobs with next_run_time <= now() will execute immediately.
        Non-blocking for AsyncIOScheduler — caller must keep event loop.
        """
        self.scheduler.start()
        log.info("ParseScheduler started")

    def shutdown(self, wait: bool = True) -> None:
        """Stop the scheduler gracefully.

        Args:
            wait: If True, wait for currently running jobs to complete.
                  If False, interrupt jobs immediately.
        """
        log.info("ParseScheduler shutdown")
        self.scheduler.shutdown(wait=wait)
        log.info("ParseScheduler stopped")
