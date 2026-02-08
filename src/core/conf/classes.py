from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import AliasPath, BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

type LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
type SourceType = Literal["HH", "HABR"]


class BaseSettingsConfig(BaseSettings):
    """Base settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        toml_file=["pyproject.toml", "settings.toml"],
        case_sensitive=False,
        validate_default=True,
        extra="ignore",
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
    directory: Path = Path("logs")
    log_file: str = "app.log"


class ProjectSettings(BaseModel):
    """Pyproject information."""

    name: str = "unknown"
    version: str = "unknown"
    description: str = "unknown"


class ObserverSchedulerSettings(BaseModel):
    """Application settings."""

    time_zone: ZoneInfo = ZoneInfo("UTC")


class SourceSettings(BaseModel):
    """Source settings."""

    url: str
    source_type: SourceType
    period_minutes: int


class ObserverSettings(BaseSettingsConfig):
    """Application settings."""

    project: ProjectSettings
    scheduler: ObserverSchedulerSettings
    sources: list[SourceSettings]

    logging: LoggingSettings = Field(
        validation_alias=AliasPath("observer", "logging")
    )


class TgBotConfig(BaseModel):
    """Telegram bot settings."""

    token: str
    user_ids: list[int]


class TgBotSettings(BaseSettingsConfig):
    """Telegram bot settings."""

    tg_bot: TgBotConfig

    logging: LoggingSettings = Field(
        validation_alias=AliasPath("tg_bot", "logging")
    )
