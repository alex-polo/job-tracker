import logging
from datetime import datetime
from typing import TYPE_CHECKING

from playwright.async_api._generated import Locator

from src.services.observer.entity import VacanciesList, VacancyEntity

from .base import BasePlaywrightLoader

if TYPE_CHECKING:
    from playwright.async_api._generated import Locator, Page


log = logging.getLogger(__name__)


class HeadHunterLoader(BasePlaywrightLoader):
    """Loader implementation using Playwright for web automation.

    This loader handles dynamic content rendering and provides robust
    scraping capabilities using browser-level interactions.
    """

    async def _parse_html(self, page: Page) -> VacanciesList:
        """Extracts vacancy data from the current page DOM.

        Args:
            page (Page): The Playwright page object with loaded content.

        Returns:
            VacanciesList: A collection of parsed VacancyEntity objects.
        """
        vacancies_list = VacanciesList()

        content: Locator = page.locator(
            "main.vacancy-serp-content div.vacancy-info--ieHKDTkezpEj0Gsx"
        )

        elements: list[Locator] = await content.all()
        log.debug("Found %d vacancy elements on the page", len(elements))

        for index, vacancy in enumerate(elements, start=1):
            # 1. Job title and link
            title_anchor: Locator = vacancy.locator(
                '[data-qa="serp-item__title"]'
            )
            title: str = await title_anchor.inner_text()
            link: str | None = await title_anchor.get_attribute("href")

            log.debug("Parsing vacancy #%d: %s", index, title)

            # 2. Salary
            salary: str = await vacancy.locator(
                ".compensation-labels--vwum2s12fQUurc2J"
            ).inner_text()

            # 3. Experience
            experience: str = await vacancy.locator(
                '[data-qa*="vacancy-serp__vacancy-work-experience"]'
            ).inner_text()

            # 4. Company
            company: str = await vacancy.locator(
                '[data-qa="vacancy-serp__vacancy-employer-text"]'
            ).inner_text()

            # 5. Location and Metro
            location: str = await vacancy.locator(
                '[data-qa="vacancy-serp__vacancy-address"]'
            ).inner_text()

            metro_locator: Locator = vacancy.locator(
                '[data-qa="address-metro-station-name"]'
            )
            metro: str = (
                await metro_locator.first.inner_text()
                if await metro_locator.count() > 0
                else "Not specified"
            )

            # 6. Snippets
            resp_loc: Locator = vacancy.locator(
                '[data-qa="vacancy-serp__vacancy_snippet_responsibility"]'
            )
            req_loc: Locator = vacancy.locator(
                '[data-qa="vacancy-serp__vacancy_snippet_requirement"]'
            )

            responsibility: str = (
                await resp_loc.inner_text()
                if await resp_loc.count() > 0
                else ""
            )
            requirement: str = (
                await req_loc.inner_text() if await req_loc.count() > 0 else ""
            )

            current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M")

            vacancies_list.append(
                VacancyEntity(
                    title=title,
                    company=company,
                    salary=salary,
                    experience=experience,
                    description=f"{responsibility}\n\n{requirement}".strip(),
                    link=link if link else "",
                    location=f"{location} (Metro: {metro})",
                    date=current_datetime,
                )
            )

        log.debug("Successfully parsed %d vacancies", len(vacancies_list))
        return vacancies_list
