from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.observer.entity import VacancyEntity


class IMessageSender(ABC):
    """Base class for message senders."""

    @abstractmethod
    async def send_message(self, vacancy: VacancyEntity) -> bool:
        """Send a message to the message broker."""
        ...
