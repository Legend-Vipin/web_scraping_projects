"""Centralized configuration management using environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent.parent / "config" / ".env")


@dataclass
class Config:
    """Application configuration loaded from environment variables."""
    
    # Project paths
    root_dir: Path
    data_dir: Path
    logs_dir: Path
    config_dir: Path
    
    # Environment
    environment: str
    debug: bool
    
    # Scraper settings
    headless: bool
    max_pages: int
    request_timeout: int
    request_delay_min: float
    request_delay_max: float
    max_retries: int
    
    # Browser settings
    browser_locale: str
    browser_timezone: str
    block_images: bool
    
    # Output settings
    output_format: str
    
    def __post_init__(self):
        """Create necessary directories after initialization."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables with defaults."""
        root_dir = Path(__file__).parent.parent.parent
        
        return cls(
            # Paths
            root_dir=root_dir,
            data_dir=Path(os.getenv("DATA_DIR", root_dir / "data")),
            logs_dir=Path(os.getenv("LOGS_DIR", root_dir / "logs")),
            config_dir=root_dir / "config",
            
            # Environment
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            
            # Scraper settings
            headless=os.getenv("HEADLESS", "true").lower() == "true",
            max_pages=int(os.getenv("MAX_PAGES", "5")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "60")),
            request_delay_min=float(os.getenv("REQUEST_DELAY_MIN", "2.0")),
            request_delay_max=float(os.getenv("REQUEST_DELAY_MAX", "5.0")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            
            # Browser settings
            browser_locale=os.getenv("BROWSER_LOCALE", "en-IN"),
            browser_timezone=os.getenv("BROWSER_TIMEZONE", "Asia/Kolkata"),
            block_images=os.getenv("BLOCK_IMAGES", "true").lower() == "true",
            
            # Output settings
            output_format=os.getenv("OUTPUT_FORMAT", "both"),
        )


# Global configuration instance
config = Config.from_env()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config
