import enum
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal, Self
from zoneinfo import ZoneInfo

from pydantic import AliasPath, BaseModel, Field, HttpUrl, computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

if TYPE_CHECKING:
    from aio_pika import ExchangeType
    from pamqp.common import FieldValue

type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class SourceType(enum.Enum):
    """Source type."""

    HH = "HH"
    HABR = "HABR"


class BaseSettingsConfig(BaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        toml_file=["pyproject.toml", "settings.toml"],
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
        frozen=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customise sources for settings."""
        return (
            TomlConfigSettingsSource(settings_cls),
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


class LoggingSettings(BaseModel):
    """Logging settings."""

    log_level: LogLevel = "DEBUG"
    log_format: str = "%(asctime)s %(levelname)6s %(name)s: %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"
    sentry_dsn: HttpUrl | None = None
    sentry_environment: str = "local"
    sentry_traces_sample_rate: float = 1.0
    sentry_log_level: LogLevel = "INFO"


class ProjectSettings(BaseModel):
    """Pyproject information."""

    name: str = "unknown"
    version: str = "unknown"
    description: str = "unknown"


class ScrapperSchedulerSettings(BaseModel):
    """Application settings."""

    time_zone: ZoneInfo = ZoneInfo("UTC")


class SourceSettings(BaseModel):
    """Source settings."""

    url: str
    tag: str
    source_type: SourceType
    search_keywords: str
    period_minutes: int
    resume: Path

    @property
    def resume_text(self) -> str:
        """Get resume text."""
        with self.resume.open(encoding="utf-8") as f:
            return f.read()


class HttpxSettings(BaseModel):
    """HTTPX settings."""

    timeout: float = 30.0
    follow_redirects: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"  # noqa: E501
    max_connections: int = 10
    max_keepalive_connections: int = 5
    verify: bool = True
    http2: bool = False


class AIAnalystSettings(BaseModel):
    """AI Analyst settings."""

    base_url: str
    api_key: str
    model: str


class ScrapperSettings(BaseSettingsConfig):
    """Application settings."""

    ENVIRONMENT: str
    project: ProjectSettings
    scheduler: ScrapperSchedulerSettings
    ai_analyst: AIAnalystSettings
    sources: list[SourceSettings]
    httpx_settings: HttpxSettings = Field(
        default=..., validation_alias=AliasPath("scrapper", "httpx_settings")
    )
    logging: LoggingSettings = Field(
        default=..., validation_alias=AliasPath("scrapper", "logging")
    )


class TgBotConfig(BaseModel):
    """Telegram bot settings."""

    token: str
    user_ids: list[int]
    environment: str


class TgBotSettings(BaseSettingsConfig):
    """Telegram bot settings."""

    tg_bot: TgBotConfig

    logging: LoggingSettings = Field(
        default=..., validation_alias=AliasPath("tg_bot", "logging")
    )


class DatabaseSettings(BaseSettingsConfig):
    """Database settings configuration."""

    _instance: ClassVar[Self | None] = None

    database_path: Path = Field(
        default=...,
        validation_alias=AliasPath(
            "database",
            "database_path",
        ),
    )
    echo: bool = Field(
        default=False,
        validation_alias=AliasPath(
            "database",
            "echo",
        ),
    )
    echo_pool: bool = Field(
        default=False,
        validation_alias=AliasPath(
            "database",
            "echo_pool",
        ),
    )
    autoflush: bool = Field(
        default=False,
        validation_alias=AliasPath(
            "database",
            "autoflush",
        ),
    )
    expire_on_commit: bool = Field(
        default=False,
        validation_alias=AliasPath(
            "database",
            "expire_on_commit",
        ),
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def naming_convention(self) -> dict[str, str]:
        """SQLAlchemy naming convention."""
        return {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # noqa: E501
            "pk": "pk_%(table_name)s",
        }

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_uri(self) -> str:
        """Get SQLite connection URI."""
        return f"sqlite+aiosqlite:///{self.database_path.as_posix()}"

    def __new__(cls, *args: object, **kwargs: object) -> Self:
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance.__init__(*args, **kwargs)  # type: ignore

            if cls._instance.database_path:
                db_dir: Path = cls._instance.database_path.parent
                db_dir.mkdir(parents=True, exist_ok=True)

        return cls._instance


class RabbitMQSettings(BaseSettingsConfig):
    """RabbitMQ settings."""

    url: str = Field(validation_alias="RABBITMQ__URL")
    connection_ttl: int = Field(
        default=...,
        validation_alias=AliasPath("rabbitmq", "connection_ttl"),
    )


@dataclass(frozen=True, slots=True)
class ExcangeConfig:
    """Exchange config."""

    name: str
    type: ExchangeType
    durable: bool


@dataclass(frozen=True, slots=True)
class QueueConfig:
    """Queue config."""

    name: str
    exchange_name: str
    routing_key: str
    message_ttl: int
    durable: bool
    arguments: dict[str, FieldValue]
    timeout: int
