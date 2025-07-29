from pydantic_settings import BaseSettings

from base_module.config import PgConfig


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    STORAGE_PATH: str = "/app/storage"
    DEBUG: bool = False

    SYNC_INTERVAL: int = 3600

    @property
    def database_url(self):
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    def to_pg_config(self) -> PgConfig:
        return PgConfig(
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
            debug=self.DEBUG,
        )


settings = Settings()
