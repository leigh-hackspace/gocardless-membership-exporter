from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/run/secrets')

    gocardless_environment: Literal["live", "sandbox"] = "live"
    gocardless_token: str


settings = Settings()
