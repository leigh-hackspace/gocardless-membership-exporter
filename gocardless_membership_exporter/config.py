from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gocardless_environment: Literal["live", "sandbox"] = "live"
    gocardless_token: str


settings = Settings()
