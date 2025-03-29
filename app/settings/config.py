from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # database
    DB_HOST: str = Field(default=...)
    DB_PORT: int = Field(default=...)
    DB_USER: str = Field(default=...)
    DB_DATABASE: str = Field(default=...)
    DB_PASSWORD: str = Field(default=...)

    # yandex
    YANDEX_CLIENT_ID: str = Field(default=...)
    YANDEX_CLIENT_SECRET: str = Field(default=...)
    YANDEX_OAUTH_TOKEN_URL: str = "https://oauth.yandex.ru/token"
    YANDEX_OAUTH_AUTHORIZE_URL: str = "https://oauth.yandex.ru/authorize"
    YANDEX_API_USERINFO_URL: str = "https://login.yandex.ru/info"

    JWT_SECRET_KEY: str = Field(default=...)

    API_BASE_URL: str = Field(default=...)

    @property
    def yandex_redirect_uri(self) -> str:
        return f"{self.API_BASE_URL}/api/users/yandex/callback"

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"


config = Config()
