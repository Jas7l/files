from pydantic_settings import BaseSettings


# Use .env to change settings
class Settings(BaseSettings):
    STORAGE_PATH: str = "./storage"
    DATABASE_URL: str = "sqlite:///./files.db"
    DEBUG: bool = False
    APP_NAME: str = "File Manager API"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
