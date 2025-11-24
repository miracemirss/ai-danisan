# app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Database ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ai_danisan"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "Emir1234**"

    # --- JWT Ayarları ---
    JWT_SECRET_KEY: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 gün

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
