"""Configuration for MCP Server"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    
    ws_host: str = "0.0.0.0"
    ws_port: int = 9001
    ws_api_key: str = "change-me"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
