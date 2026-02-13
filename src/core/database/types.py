from __future__ import annotations

from datetime import datetime
from typing import Annotated

from sqlalchemy import TIMESTAMP, String, func
from sqlalchemy.orm import mapped_column

from src.core.utils import utcnow

IntPk = Annotated[
    int,
    mapped_column(primary_key=True),
]

UniqueStr64 = Annotated[
    str,
    mapped_column(String(length=64), unique=True, index=True),
]

CreatedAt = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        default=utcnow,
        server_default=func.now(),
    ),
]
UpdatedAt = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        server_onupdate=func.now(),
    ),
]

__all__ = (
    "CreatedAt",
    "IntPk",
    "UniqueStr64",
    "UpdatedAt",
)
