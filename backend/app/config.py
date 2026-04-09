# DemocratIA - Application configuration

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://democratia:democratia_secret@db:5432/democratia"
    GROQ_API_KEY: str = ""
    CORS_ORIGINS: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
