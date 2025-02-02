from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str
    group_id: int
    base_vk_api_url: str
    vk_api_version: str
    random_id: int = 0
    long_poll_wait: int = 10
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
