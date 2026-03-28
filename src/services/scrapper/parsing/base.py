from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.scrapper.entity import VacanciesList


class IParser(ABC):
    """Interface for parsing HTML data."""

    @abstractmethod
    def parse(self, data: str) -> VacanciesList:
        """Parse HTML data into a list of VacancyEntity objects."""
        ...
