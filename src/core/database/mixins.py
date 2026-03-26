from sqlalchemy.orm import Mapped

from .types import CreatedAt, IntPk, UpdatedAt


class IntIdMixin:
    """Mixin for models with an integer primary key."""

    id: Mapped[IntPk]


class TimestampMixin:
    """Mixin for models with a created_at and updated_at columns."""

    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]
