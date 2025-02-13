from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    map_width: int = 10
    map_height: int = 16
