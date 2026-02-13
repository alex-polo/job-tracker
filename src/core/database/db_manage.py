from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Final

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.conf.classes import DatabaseSettings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio.engine import AsyncEngine


class DatabaseManager:
    """Manages database connections and session lifecycle.

    This class initializes the SQLAlchemy async engine and provides
    a thread-safe session factory, specifically optimized for SQLite.
    """

    def __init__(self, db_settings: DatabaseSettings) -> None:
        """Initialize the database engine and session maker.

        Args:
            db_settings (DatabaseSettings): configuration object.
        """
        self._async_engine: AsyncEngine = create_async_engine(
            url=db_settings.database_uri,
            echo=db_settings.echo,
            echo_pool=db_settings.echo_pool,
            connect_args={"timeout": 30},
        )

        self._async_session_maker: async_sessionmaker[AsyncSession] = (
            async_sessionmaker(
                bind=self._async_engine,
                autoflush=db_settings.autoflush,
                expire_on_commit=db_settings.expire_on_commit,
            )
        )

    async def dispose_engine(self) -> None:
        """Gracefully close all database connections in the pool.

        Should be called during application shutdown.
        """
        await self._async_engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        """Provide a transactional scope around a series of operations.

        Automatically handles commit on success, rollback on error,
        and ensures the session is closed.

        Yields:
            AsyncSession: An active SQLAlchemy asynchronous session.

        Raises:
            Exception: Re-raises any exception occurred during the transaction
                after performing a rollback.
        """
        async with self._async_session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


DB_MANAGER: Final[DatabaseManager] = DatabaseManager(
    db_settings=DatabaseSettings()  # type: ignore
)


# async def main():
#     # Просто вызываем контекстный менеджер
#     async with DB_MANAGER.session() as session:
#         # Сессия открыта и активна
#         new_vacancy = VacancyEntity(...)
#         session.add(new_vacancy)
#         await session.commit()
