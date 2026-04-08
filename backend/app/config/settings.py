from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB_NAME: str

    # MOIS API
    MOIS_API_BASE_URL: str

    @property
    def mongo_url(self) -> str:
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()