import logging

from sqlalchemy import exists, insert, select

from src.core.database import DB_MANAGER
from src.services.observer.models import Vacancy

from .base import IRepository

log = logging.getLogger(__name__)


class VacancyRepository(IRepository):
    """Vacancy repository."""

    async def exists(self, vacancy_hash: str) -> bool:
        """Check if vacancy exists in the repository."""
        async with DB_MANAGER.session() as session:
            query = select(exists().where(Vacancy.hash == vacancy_hash))

            result: bool | None = await session.scalar(query)

            if not result:
                return False

            return result

    async def save(self, vacancy_hash: str) -> None:
        """Save vacancy to the repository."""
        async with DB_MANAGER.session() as session:
            try:
                stmt = insert(Vacancy).values(hash=vacancy_hash)
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                log.exception("Error saving vacancy: %s", e)
