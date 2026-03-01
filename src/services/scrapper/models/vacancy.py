from __future__ import annotations

from sqlalchemy.orm import Mapped

from src.core.database import Base
from src.core.database.mixins import IntIdMixin, TimestampMixin
from src.core.database.types import UniqueStr64


class Vacancy(Base, IntIdMixin, TimestampMixin):
    """Vacancy model."""

    hash: Mapped[UniqueStr64]
