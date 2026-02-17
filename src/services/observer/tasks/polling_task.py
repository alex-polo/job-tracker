import logging

from .base_task import ISchedulerTask

log = logging.getLogger(__name__)


class PollingTask(ISchedulerTask):
    """HeadHunter Parse Task."""

    async def run(self, url: str) -> None:
        """Run task."""
        for vacancy in await self._loader.load(url=url):
            if not await self._repository.exists(vacancy_hash=vacancy.hash):
                if await self.mq_publisher.send_message(vacancy=vacancy):
                    await self._repository.save(vacancy_hash=vacancy.hash)
                else:
                    log.error(
                        "Failed to send vacancy to RabbitMQ: %s", vacancy
                    )
                log.debug("Vacancy saved: %s", vacancy.hash)
            else:
                log.debug("Vacancy already exists: %s", vacancy.hash)
