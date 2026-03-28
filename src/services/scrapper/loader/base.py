from abc import ABC, abstractmethod


class ILoader(ABC):
    """Interface for loading html data from a given source."""

    @abstractmethod
    async def load(
        self,
        url: str,
        params: dict[str, str] | None = None,
    ) -> str:
        """Download data from the source.

        Args:
           url (str): Source URL.
           params (dict[str, str] | None): URL parameters.

        Returns:
           str: Html data.
        """
        ...
