from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal

class Config(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")  
    DB_URL: str = Field(..., env="DB_URL")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    ENV: Literal["local", "docker", "prod"] = Field("local", env="ENV")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

def load_config(env: str = "local") -> Config:
    env_file = ".env" 
    return Config(_env_file=env_file)