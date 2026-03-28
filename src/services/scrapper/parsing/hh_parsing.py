import json
import logging
from datetime import datetime

from src.services.scrapper.entity import VacanciesList, VacancyEntity
from src.services.scrapper.exceptions import ScrapperParsingError
from src.services.scrapper.parsing.base import IParser

log = logging.getLogger(__name__)


class HeadHunterParser(IParser):
    """HH.ru vacancy search results parser."""

    def del_highlighttext(self, data: str) -> str:
        """Remove highlighttext from the data."""
        new_data = data.replace(
            "<highlighttext>",
            "",
        ).replace(
            "</highlighttext>",
            "",
        )

        return new_data.strip()

    def parse(self, data: str) -> VacanciesList:
        """Parse HH.ru vacancy search results."""
        vacancies_list = VacanciesList()
        json_data = json.loads(data)

        json_vacancies_list = json_data.get("items", None)

        if not json_vacancies_list:
            raise ScrapperParsingError("No vacancies found")

        for json_item in json_vacancies_list:
            try:
                title: str = json_item.get("name")
                company = json_item.get("employer", {}).get("name")

                salary_raw = json_item.get("salary")

                if salary_raw:
                    salary_from = salary_raw.get("from") or "N/A"
                    salary_to = salary_raw.get("to") or "N/A"

                    salary = f"{salary_from} - {salary_to}"

                    if salary_raw.get("currency"):
                        salary += f" {salary_raw.get('currency') or ''}"

                else:
                    salary = "Не указана"  # noqa: RUF001

                experience = json_item.get("experience", {}).get("name")
                description = ""

                snippet = json_item.get("snippet", {})
                if snippet.get("requirement"):
                    description += f"{snippet.get('requirement')}\n"

                if snippet.get("responsibility"):
                    description += f"\n{snippet.get('responsibility')}\n"

                link = json_item.get("alternate_url")
                location = json_item.get("area", {}).get("name")

                date_obj = datetime.fromisoformat(
                    json_item.get("published_at")
                )
                date = date_obj.strftime("%d.%m.%Y %H:%M")

                vacancies_list.append(
                    VacancyEntity(
                        title=self.del_highlighttext(title),
                        company=self.del_highlighttext(company),
                        salary=salary,
                        experience=self.del_highlighttext(experience),
                        description=self.del_highlighttext(description),
                        link=link,
                        location=self.del_highlighttext(location),
                        date=date,
                        raw_data=json_item,
                    )
                )
            except Exception as e:
                raise ScrapperParsingError(
                    f"Error parsing vacancy: {e}"
                ) from e

        return vacancies_list
