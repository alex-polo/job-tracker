from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.observer.loaders import ILoader
    from src.services.observer.repositories import IRepository


class ISchedulerTask(ABC):
    """Interface for scheduler tasks."""

    def __init__(self, loader: ILoader, repository: IRepository) -> None:
        """Initialize task."""
        self._loader = loader
        self._repository = repository

    @abstractmethod
    async def run(self) -> None:
        """Run task."""
