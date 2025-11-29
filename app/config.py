from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_title: str = "Social Network API"
    api_description: str = "REST API for Social Network Application"
    api_version: str = "1.0.0"

    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "social_network"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"

    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://yourdomain.com",
    ]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes

    # Compression Configuration
    compression_enabled: bool = True
    compression_min_size: int = 1000

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
