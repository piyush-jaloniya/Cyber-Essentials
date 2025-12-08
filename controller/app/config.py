"""Configuration settings for the controller"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "CE-Controller"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str  # Required - must be set via environment variable
    # For development with SQLite: "sqlite:///./ce_controller.db"
    # For PostgreSQL: "postgresql://ce_user:PASSWORD@localhost:5432/ce_controller"
    
    # Security
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_RANDOM_STRING"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    agent_token_expire_days: int = 365
    
    # API
    api_prefix: str = "/api"
    
    # CORS
    cors_origins: list = []  # Set via environment variable for security
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
