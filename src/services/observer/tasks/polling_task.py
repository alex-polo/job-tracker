import logging

from .base_task import ISchedulerTask

log = logging.getLogger(__name__)


class PollingTask(ISchedulerTask):
    """A task for periodically polling the HH.ru API.

    Loads vacancies from a specified URL, checks their existence in the db,
    and publishes new vacancies to RabbitMQ.
    """

    async def run(self, url: str) -> None:
        """Execute the polling task.

        Loads vacancies, checks if they exist in the repository,
        and sends new vacancies to the message queue.

        Args:
            url: The URL to fetch vacancies from API.
        """
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
