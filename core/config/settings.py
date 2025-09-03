import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = "Astral Assessment API"
    debug: bool = False
    
    # External API Keys (optional for free tiers)
    firecrawl_api_key: Optional[str] = "your_key"
    openai_api_key: Optional[str] = None
    inngest_event_key: Optional[str] = "your_key"
    inngest_signing_key: Optional[str] = "your_key"
    
    # Paths
    output_dir: Path = Path("outputs")
    
    # Rate limiting and processing limits
    max_urls_to_scrape: int = 10
    max_content_length: int = 50000  # characters
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)


settings = Settings()