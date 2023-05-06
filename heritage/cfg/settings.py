from pydantic import BaseSettings


class Settings(BaseSettings):
    tg_token: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
