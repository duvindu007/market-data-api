from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    # API
    EXTERNAL_API_URL: str
    API_KEY: str
    API_TIMEOUT: int

    # Database
    DB_NAME: str 

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    model_config = SettingsConfigDict(env_file=".env")


# singleton instance
settings = Settings()

