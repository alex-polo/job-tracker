from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.observer.loaders import ILoader
    from src.services.observer.messaging.rabbitmq import MQPublisher
    from src.services.observer.repositories import IRepository


class ISchedulerTask(ABC):
    """Interface for scheduler tasks."""

    def __init__(
        self,
        loader: ILoader,
        repository: IRepository,
        mq_publisher: MQPublisher,
    ) -> None:
        """Initialize task."""
        self._loader = loader
        self._repository = repository
        self.mq_publisher: MQPublisher = mq_publisher

    @abstractmethod
    async def run(self) -> None:
        """Run task."""
