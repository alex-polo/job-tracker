from abc import ABC, abstractmethod


class IRepository(ABC):
    """Interface for repository."""

    @abstractmethod
    async def exists(self, vacancy_hash: str) -> bool:
        """Check if vacancy exists in the repository."""

    @abstractmethod
    async def save(self, vacancy_hash: str) -> None:
        """Save vacancy to the repository."""
