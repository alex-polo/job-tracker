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

    Loads vacancies from a specified URL, checks their existence in db,
    and publishes new vacancies to RabbitMQ.
    """

    def __init__(
        self,
        url: str,
        request_params: dict[str, str],
        main_tag: str,
        tags: list[str],
        loader: ILoader,
        parser: IParser,
        repository: IRepository,
        mq_publisher: MQPublisher,
    ) -> None:
        """Initialize task."""
        self._loader = loader
        self._parser = parser
        self._repository = repository
        self._mq_publisher = mq_publisher
        self._url = url
        self._main_tag = main_tag
        self._tags = tags
        self._request_params = request_params

    async def run(self) -> None:
        """Execute the polling task.

        Loads vacancies, checks if they exist in the repository,
        and sends new vacancies to the message queue.

        Args:
            url: The URL to fetch vacancies from API.
        """
        log.info("Polling task started for URL: %s", self._url)
        try:
            log.info("Loading HTML data from source")
            download_data: str = await self._loader.load(
                url=self._url,
                params=self._request_params,
            )
            log.info("Data loaded, size: %d bytes", len(download_data))

            log.info("Parsing vacancies from HTML")
            vacancies_list: VacanciesList = self._parser.parse(
                data=download_data,
            )
            log.info("Parsed %d vacancies from source", len(vacancies_list))

            for vacancy in vacancies_list:
                if not await self._repository.exists(
                    vacancy_hash=vacancy.hash
                ):
                    log.info(
                        "Processing new vacancy: %s at %s",
                        vacancy.title,
                        vacancy.link,
                    )
                    vacancy.main_tag = self._main_tag
                    vacancy.tags = self._tags

                    if await self._mq_publisher.send_message(vacancy=vacancy):
                        await self._repository.save(vacancy_hash=vacancy.hash)
                        log.info(
                            "Vacancy saved and published: %s", vacancy.hash
                        )
                    else:
                        log.error(
                            "Failed to send vacancy to RabbitMQ: %s", vacancy
                        )
                else:
                    log.info("Vacancy already exists: %s", vacancy.hash)

        except Exception as e:
            log.exception("Error occurred during polling: %s", e)
            raise
