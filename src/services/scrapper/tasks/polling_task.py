from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .base_task import ISchedulerTask

if TYPE_CHECKING:
    from src.services.scrapper.entity import VacanciesList
    from src.services.scrapper.loader.base import ILoader
    from src.services.scrapper.messaging.rabbitmq import MQPublisher
    from src.services.scrapper.parsing.base import IParser
    from src.services.scrapper.repositories.base import IRepository

log = logging.getLogger(__name__)


class PollingTask(ISchedulerTask):
    """A task for periodically polling the HH.ru API.

    Loads vacancies from a specified URL, checks their existence in the db,
    and publishes new vacancies to RabbitMQ.
    """

    def __init__(
        self,
        loader: ILoader,
        parser: IParser,
        repository: IRepository,
        mq_publisher: MQPublisher,
    ) -> None:
        """Initialize task."""
        self._loader = loader
        self._parser = parser
        self._repository = repository
        self.mq_publisher = mq_publisher

    async def run(self, url: str) -> None:
        """Execute the polling task.

        Loads vacancies, checks if they exist in the repository,
        and sends new vacancies to the message queue.

        Args:
            url: The URL to fetch vacancies from API.
        """
        html_data: str = await self._loader.load(url=url)
        vacancies_list: VacanciesList = self._parser.parse(html_data)
        for vacancy in vacancies_list:
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
