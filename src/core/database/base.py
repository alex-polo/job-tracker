from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
)

from src.core.conf.classes import DatabaseSettings
from src.core.utils import camel_to_snake

from .mixins import IntIdMixin


class Base(AsyncAttrs, DeclarativeBase, IntIdMixin):
    """Base class for all models."""

    __abstract__ = True

    metadata = MetaData(
        naming_convention=DatabaseSettings().naming_convention,  # type: ignore
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Return the table name for the model."""
        return camel_to_snake(cls.__name__)
