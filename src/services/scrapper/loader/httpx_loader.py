import logging
from typing import TYPE_CHECKING

import httpx

from src.services.scrapper.exceptions import ScrapperDownloadError
from src.services.scrapper.loader.base import ILoader

if TYPE_CHECKING:
    from src.core.conf.classes import HttpxSettings

log = logging.getLogger(__name__)


class HttpxLoader(ILoader):
    """HTTP loader implementation using httpx client.

    Provides async HTTP/2 capable page loading with configurable
    connection pooling and request settings.
    """

    def __init__(self, settings: HttpxSettings) -> None:
        """Initialize the loader with HTTP settings.

        Args:
            settings: HTTP client configuration including timeout,
                headers, connection limits, and TLS options.
        """
        self._settings = settings

    async def load(self, url: str) -> str:
        """Fetch HTML content from the specified URL.

        Args:
            url: The URL to fetch content from.

        Returns:
            Raw HTML response text.

        Raises:
            ScrapperDownloadError: If HTTP request fails or returns
                an error status code.
        """
        async with httpx.AsyncClient(
            timeout=self._settings.timeout,
            follow_redirects=self._settings.follow_redirects,
            verify=self._settings.verify,
            http2=self._settings.http2,
            headers={
                "User-Agent": self._settings.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  # noqa: E501
            },
            limits=httpx.Limits(
                max_connections=self._settings.max_connections,
                max_keepalive_connections=self._settings.max_keepalive_connections,
            ),
        ) as client:
            try:
                response = await client.get(url)
                log.info("Response status code: %s", response.status_code)
                response.raise_for_status()
                return response.text
            except Exception as e:
                log.error("Download error: %s", e)
                raise ScrapperDownloadError(f"HTTP error: {e}") from e
