from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    map_width: int = 5
    map_height: int = 8
