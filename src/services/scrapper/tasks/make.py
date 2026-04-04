from typing import TYPE_CHECKING

from src.services.scrapper.loader.httpx_loader import HttpxLoader
from src.services.scrapper.parsing.hh_parsing import HeadHunterParser
from src.services.scrapper.repositories.vacancy import VacancyRepository
from src.services.scrapper.tasks.polling_task import PollingTask

if TYPE_CHECKING:
    from src.core.conf.classes import (
        HttpxSettings,
        SourceSettings,
    )
    from src.services.scrapper.ai_analyst.analyst import VacancyAIAnalyst
    from src.services.scrapper.messaging.rabbitmq import MQPublisher
    from src.services.scrapper.tasks.base_task import ISchedulerTask


def make_headhunter_polling_task(
    source_settings: SourceSettings,
    ai_analyst: VacancyAIAnalyst,
    mq_publisher: MQPublisher,
    loader_settings: HttpxSettings,
) -> ISchedulerTask:
    """Create a polling task instance.

    Args:
        source_settings: Source settings.
        ai_analyst: AI Analyst instance.
        mq_publisher: The RabbitMQ publisher instance.
        loader_settings: HTTPX settings.

    Returns:
        A configured PollingTask instance.
    """
    search_url = f"{source_settings.url}/vacancies"

    params: dict[str, str] = {
        "text": " OR ".join(source_settings.search_keywords.split(","))
    }
    params["order_by"] = "publication_time"
    params["per_page"] = "50"

    tags_string: str = "#".join(source_settings.search_keywords.split(","))
    tags: list[str] = ["#" + tag for tag in tags_string.split("#") if tag]

    return PollingTask(
        loader=HttpxLoader(settings=loader_settings),
        parser=HeadHunterParser(),
        repository=VacancyRepository(),
        mq_publisher=mq_publisher,
        ai_analyst=ai_analyst,
        main_tag=source_settings.tag,
        url=search_url,
        request_params=params,
        tags=tags,
        resume=source_settings.resume_text,
    )
