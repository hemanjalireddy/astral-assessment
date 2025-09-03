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
    firecrawl_api_key: Optional[str] = "fc-f8d98468417c4795bc9410dcae7f6355"
    openai_api_key: Optional[str] = None
    inngest_event_key: Optional[str] = "WS1ZQ82CJU7e0Lm8u3vi3WfmHYV0Mcam6bSioX1AaCEO98A8Pihj6Un102PacdGtxBcOTDqTqYmNzFr1AKMT5Q"
    inngest_signing_key: Optional[str] = "signkey-prod-4159b3eba5421ed30cddaf7bfd1c9a976e408e9f9a4a53d3edf23b89ffae22c0"
    #inngest_dev: bool = os.getenv("INNGEST_DEV", "0") == "1"
    
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