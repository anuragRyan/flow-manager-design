"""Application configuration settings.

This module manages application configuration using pydantic settings.
Configuration can be loaded from environment variables or a .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings.
    
    Settings can be overridden via environment variables.
    For example, APP_NAME can be set via the APP_NAME env var.
    """
    
    # Application settings
    app_name: str = "Flow Manager"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS settings
    cors_origins: list = ["*"]
    
    # Flow execution settings
    max_execution_history: int = 1000
    task_timeout: int = 300  # seconds
    
    # Security settings
    secret_key: str = "your-secret-key-here-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # API Key settings
    api_key_header_name: str = "X-API-Key"
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    # Security headers
    enable_security_headers: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
