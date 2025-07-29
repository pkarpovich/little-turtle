from typing import List, Annotated, Union
from pydantic import Field, field_validator, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode


def parse_int_list(v: Union[str, List[int]]) -> List[int]:
    if isinstance(v, str):
        if not v:
            return []
        return [int(x.strip()) for x in v.split(",")]
    return v


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    REDIS_URL: str = "redis://localhost:6379/0"
    BASE_IMAGE_FOLDER: str = "/app/little_turtle/images"

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE_NUMBER: str
    TELEGRAM_SESSION_NAME: str = "little_turtle"
    TELEGRAM_ALLOWED_USERS: Annotated[list[int], NoDecode]

    CHAT_IDS_TO_SEND_STORIES: Annotated[list[int], NoDecode]
    USER_IDS_TO_SEND_MORNING_MSG: Annotated[list[int], NoDecode]

    GENERATION_LANGUAGE: str = "Russian"
    DEFAULT_TZ: int = 3
    DEFAULT_SCHEDULE_HOUR: int = 6
    DEFAULT_SCHEDULE_MINUTE: int = 4
    DEFAULT_SCHEDULE_SECOND: int = 33

    PHOENIX_COLLECTOR_ENDPOINT: str = ""
    PHOENIX_PROJECT_NAME: str = "little-turtle"
    PHOENIX_ENABLED: bool = True

    APPLICATION_TZ: str = "Europe/Warsaw"
    DEBUG: bool = False
    LOGS_LEVEL: str = "INFO"
    DEV_LOGS: bool = False

    @field_validator(
        "TELEGRAM_ALLOWED_USERS",
        "CHAT_IDS_TO_SEND_STORIES",
        "USER_IDS_TO_SEND_MORNING_MSG",
        mode="before",
    )
    @classmethod
    def decode_numbers(cls, v: str) -> list[int]:
        return [int(x) for x in v.split(",")]


def create_app_config() -> AppConfig:
    """Factory function to create AppConfig instance"""
    return AppConfig()
