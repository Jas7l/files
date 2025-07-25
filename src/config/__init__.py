from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    STORAGE_PATH: str = "/app/storage"
    DEBUG: bool = False
    APP_NAME: str = "File Manager API"
    VERSION: str = "1.0.0"

    @property
    def database_url(self):
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    class Config:
        env_file = ".env"


settings = Settings()
