from abc import ABC, abstractmethod


class ISchedulerTask(ABC):
    """Interface for scheduler tasks."""

    @abstractmethod
    async def run(self) -> None:
        """Run task."""
