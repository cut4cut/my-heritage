from pydantic import BaseSettings


class Settings(BaseSettings):
    tg_token: str = ""
    admin_chat_id: int = -1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
