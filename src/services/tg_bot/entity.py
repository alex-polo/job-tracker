import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

log = logging.getLogger(__name__)


class IReceivedConsumedMessage(ABC):
    """Abstract base interface for received consumed messages.

    This interface defines the contract for message entities that can be
    formatted for display in Telegram and deserialized from JSON bytes.

    Attributes:
        format_message: Abstract method to format the message for Telegram.
        from_json: Abstract class method to create instance from JSON bytes.
    """

    @abstractmethod
    def format_message(self) -> str:
        """Format message content for display in Telegram bot.

        Returns:
            str: Formatted message text with HTML/Markdown formatting.
        """

    @classmethod
    @abstractmethod
    def from_json(cls, json_bytes: bytes) -> Self:
        """Parse JSON bytes and create entity instance.

        Args:
            json_bytes: Raw JSON bytes containing message data.

        Returns:
            Self: New instance of the implementing class.
        """


@dataclass(frozen=True, slots=True)
class RecivedVacancyEntity(IReceivedConsumedMessage):
    """Entity representing a received vacancy.

    This dataclass encapsulates vacancy information and provides methods
    to format it for Telegram display and create inline keyboards.

    Attributes:
        title: Job title/position name.
        company: Company name offering the position.
        salary: Salary information (range or fixed amount).
        experience: Required work experience level.
        description: Detailed job description.
        link: URL to apply for the position or view details.
        location: Geographic location of the position.
        date: Date when the vacancy was posted.
    """

    title: str
    company: str
    salary: str
    experience: str
    description: str
    link: str
    location: str
    date: str

    def create_keyboard(self) -> InlineKeyboardMarkup:
        """Create inline keyboard with action button.

        Creates an inline keyboard markup with a single button
        that links to the vacancy application page.

        Returns:
            InlineKeyboardMarkup: Keyboard with 'Подробнее' button.
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📌 Подробнее", url=self.link)]
            ]
        )

    def format_message(self) -> str:
        """Format vacancy data as HTML message.

        Creates a formatted text message with vacancy details including
        title, company, salary, location, experience requirements, and
        description. Uses HTML formatting for bold title.

        Returns:
            str: Formatted vacancy message ready for Telegram.
        """
        return (
            f"<b>{self.title}</b>\n\n"
            f"Компания: {self.company}\n"
            f"З/П: {self.salary}\n"  # noqa: RUF001
            f"Локация: {self.location}\n"
            f"Опыт работы: {self.experience}\n"
            f"Дата: {self.date}\n\n"
            f"Описание:\n{self.description}\n\n"
        )

    @classmethod
    def from_json(cls, json_bytes: bytes) -> Self:
        """Create vacancy entity from JSON bytes.

        Parses JSON data and extracts vacancy fields with fallback
        to 'unoknown' for missing fields.

        Args:
            json_bytes: Raw JSON bytes containing vacancy data.

        Returns:
            Self: New RecivedVacancyEntity instance.
        """
        log.debug("Parsing vacancy JSON: %s", json_bytes)
        data: dict[str, str] = json.loads(json_bytes.decode("utf-8"))
        log.debug("Parsed vacancy data: %s", data)

        title: str = data.get("title", "unoknown")
        company: str = data.get("company", "unoknown")
        salary: str = data.get("salary", "unoknown")
        experience: str = data.get("experience", "unoknown")
        description: str = data.get("description", "unoknown")
        link: str = data.get("link", "unoknown")
        location: str = data.get("location", "unoknown")
        date: str = data.get("date", "unoknown")

        entity = cls(
            title=title,
            company=company,
            salary=salary,
            experience=experience,
            description=description,
            link=link,
            location=location,
            date=date,
        )
        log.debug("Created RecivedVacancyEntity: %s", entity)
        return entity

    def __repr__(self) -> str:
        """Return string representation of the entity."""
        return (
            f"RecivedVacancyEntity(title={self.title!r}, "
            f"company={self.company!r}, "
            f"salary={self.salary!r}, "
            f"location={self.location!r}, "
            f"link={self.link!r})"
        )


__all__ = ("IReceivedConsumedMessage", "RecivedVacancyEntity")
