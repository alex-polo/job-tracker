from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.scrapper.entity import VacanciesList


class IParser(ABC):
    """Interface for parsing HTML data into a list of VacancyEntity objects."""

    @abstractmethod
    def parse(self, html_data: str) -> VacanciesList:
        """Parse HTML data into a list of VacancyEntity objects."""
        ...
