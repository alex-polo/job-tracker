import logging
from datetime import datetime

from bs4 import BeautifulSoup, Tag

from src.services.scrapper.entity import VacanciesList, VacancyEntity
from src.services.scrapper.exceptions import ScrapperParsingError
from src.services.scrapper.parsing.base import IParser

from .bs_utils import get_href_attr, get_tag, get_text

log = logging.getLogger(__name__)


class HeadHunterParser(IParser):
    """HH.ru vacancy search results parser."""

    def parse(self, data: str) -> VacanciesList:
        """Parse HH.ru vacancy search results.

        Args:
            data: HTML content from HH.ru vacancy search page.

        Returns:
            List of parsed vacancy data.
        """
        soup = BeautifulSoup(data, "html.parser")
        vacancies_items = soup.find_all(
            "div", {"data-qa": "vacancy-serp__vacancy"}
        )

        vacancies_list = VacanciesList()

        for item in vacancies_items:
            try:
                title_tag: Tag = get_tag(
                    item,
                    tag_name="h2",
                    class_="bloko-header-section-2",
                )
                url_tag: Tag = get_tag(title_tag, "a")

                title: str = get_text(title_tag)
                url: str = get_href_attr(url_tag, "href")

                company_tag = item.find(
                    "span",
                    attrs={"data-qa": "vacancy-serp__vacancy-employer-text"},
                )
                company: str = get_text(company_tag) if company_tag else ""

                responsibility_tag = item.find(
                    "div",
                    attrs={
                        "data-qa": "vacancy-serp__vacancy_snippet_responsibility"
                    },
                )
                requirement_tag = item.find(
                    "div",
                    attrs={
                        "data-qa": "vacancy-serp__vacancy_snippet_requirement"
                    },
                )
                description_parts = []
                if responsibility_tag:
                    description_parts.append(get_text(responsibility_tag))
                if requirement_tag:
                    description_parts.append(get_text(requirement_tag))
                description: str = (
                    "\n\n".join(description_parts) if description_parts else ""
                )

                experience_tag = item.find(
                    "span",
                    attrs={
                        "data-qa": lambda x: bool(x and "work-experience" in x)
                    },
                )
                experience: str = (
                    get_text(experience_tag) if experience_tag else ""
                )

                location_tag = item.find(
                    "span",
                    attrs={"data-qa": "vacancy-serp__vacancy-address"},
                )
                location: str = get_text(location_tag) if location_tag else ""

                salary_tag = item.find(
                    "span",
                    attrs={"data-qa": "vacancy-serp__vacancy-salary"},
                )
                salary: str = (
                    get_text(salary_tag) if salary_tag else "Не указано"  # noqa: RUF001
                )

                current_date: str = datetime.now().strftime("%d.%m.%Y %H:%M")

                vacancies_list.append(
                    VacancyEntity(
                        title=title,
                        company=company,
                        salary=salary,
                        experience=experience,
                        description=description,
                        link=url,
                        location=location,
                        date=current_date,
                        raw_data=item.text,
                    )
                )

            except Exception as e:
                log.error("Error parsing filed vacancy: %s", e)
                log.debug("Vacancy data: %s", item)
                raise ScrapperParsingError(
                    f"Error parsing vacancy: {e}"
                ) from e

        return vacancies_list
