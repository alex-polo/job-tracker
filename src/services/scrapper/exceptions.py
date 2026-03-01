class ScrapperNBaseError(Exception):
    """Base exception for scrapper."""


class ScrapperDownloadError(ScrapperNBaseError):
    """Exception for downloading data from a source."""


class ScrapperParsingError(ScrapperNBaseError):
    """Exception for parsing data."""


__all__ = (
    "ScrapperDownloadError",
    "ScrapperParsingError",
)
