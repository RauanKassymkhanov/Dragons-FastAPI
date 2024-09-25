from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    AWS_REGION_NAME: str
    SQS_QUEUE_URL: str
    QUEUE_NAME: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    TRIGGER_SQS_QUEUE_URL: str
    TRIGGER_QUEUE_NAME: str
    S3_BUCKET_NAME: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
