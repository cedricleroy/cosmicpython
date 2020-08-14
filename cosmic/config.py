from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 8000

    def get_api_url(self) -> str:
        return "http://{}:{}".format(self.HOST, self.PORT)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
