from abc import ABC, abstractmethod


class ILoader(ABC):
    """Interface for loading html data from a given source."""

    @abstractmethod
    async def load(self, url: str) -> str:
        """Download data from the source.

        Args:
           url (str): Source URL.

        Returns:
           str: Html data.
        """
        ...
