from typing import TYPE_CHECKING

from src.services.scrapper.loader.httpx_loader import HttpxLoader
from src.services.scrapper.parsing.hh_parsing import HeadHunterParser
from src.services.scrapper.repositories.vacancy import VacancyRepository
from src.services.scrapper.tasks.polling_task import PollingTask

if TYPE_CHECKING:
    from src.core.conf.classes import HttpxSettings
    from src.services.scrapper.messaging.rabbitmq import MQPublisher
    from src.services.scrapper.tasks.base_task import ISchedulerTask


def make_headhunter_polling_task(
    main_tag: str,
    url: str,
    keywords: str,
    mq_publisher: MQPublisher,
    loader_settings: HttpxSettings,
) -> ISchedulerTask:
    """Create a polling task instance.

    Args:
        main_tag: The job tag.
        url: The URL to fetch vacancies from API.
        keywords: The keywords to search for.
        mq_publisher: The RabbitMQ publisher instance.
        loader_settings: HTTPX settings.

    Returns:
        A configured PollingTask instance.
    """
    search_url = f"{url}/vacancies"

    params = {"text": " OR ".join(keywords.split(","))}
    params["order_by"] = "publication_time"
    params["per_page"] = "50"

    tags_string = "#".join(keywords.split(","))
    tags = ["#" + tag for tag in tags_string.split("#") if tag]

    return PollingTask(
        main_tag=main_tag,
        url=search_url,
        request_params=params,
        tags=tags,
        loader=HttpxLoader(settings=loader_settings),
        parser=HeadHunterParser(),
        repository=VacancyRepository(),
        mq_publisher=mq_publisher,
    )
