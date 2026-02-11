from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.observer.entity import VacanciesList


class ILoader(ABC):
    """Interface for loading vacancies from a given source."""

    @abstractmethod
    async def receiving_vacancies(self, url: str) -> VacanciesList:
        """Receive vacancies from the source.

        Args:
           url (str): Source URL.

        Returns:
           VacanciesList: List of vacancies.
        """
