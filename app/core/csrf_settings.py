from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CsrfSettings(BaseSettings):
    secret_key: str = Field(validation_alias="CSRF_SECRET_KEY")
    cookie_samesite: str = Field(validation_alias="COOKIE_SAMESITE")
    cookie_secure: bool = Field(validation_alias="COOKIE_SECURE")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


crsf_settings = CsrfSettings()
