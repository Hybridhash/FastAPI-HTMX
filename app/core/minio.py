from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    minio_url: str = Field(validation_alias="MINIO_URL")
    minio_access_key: str = Field(alias="MINIO_ACCESS_KEY")
    minio_scret_key: str = Field(alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(alias="MINIO_BUCKET")

    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )


print(Settings().model_dump())
