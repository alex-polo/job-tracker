import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from playwright.async_api import async_playwright

from src.services.observer.entity import VacanciesList

if TYPE_CHECKING:
    from playwright.async_api._generated import Browser, Page

    from src.services.observer.entity import VacanciesList

log = logging.getLogger(__name__)


class ILoader(ABC):
    """Interface for loading vacancies from a given source."""

    @abstractmethod
    async def load(self, url: str) -> VacanciesList:
        """Receive vacancies from the source.

        Args:
           url (str): Source URL.

        Returns:
           VacanciesList: List of vacancies.
        """


class BasePlaywrightLoader(ILoader):
    """Base class for Playwright-based loaders."""

    @abstractmethod
    async def _parse_html(self, page: Page) -> VacanciesList:
        """Extracts vacancy data from the current page DOM.

        Args:
            page (Page): The Playwright page object with loaded content.

        Returns:
            VacanciesList: A collection of parsed VacancyEntity objects.
        """

    async def load(self, url: str) -> VacanciesList:
        """Initializes the browser, navigates to the URL, and triggers parsing.

        Uses async_playwright context manager to ensure all browser resources
        are properly closed after execution or in case of an error.

        Args:
            url (str): The search results URL to parse.

        Returns:
            VacanciesList: The list of extracted vacancies.
        """
        log.debug("Starting Playwright automation for URL: %s", url)

        async with async_playwright() as p:
            log.debug("Launching Chromium browser")
            browser: Browser = await p.chromium.launch(headless=True)

            page: Page = await browser.new_page()

            log.debug("Navigating to page...")
            await page.goto(url)

            log.debug("Waiting for network idle state")
            await page.wait_for_load_state("networkidle")

            result = await self._parse_html(page)

            log.debug("Browser session closing automatically")
            return result
