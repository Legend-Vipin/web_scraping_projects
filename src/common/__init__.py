"""Common utilities for web scraping projects."""

# Logger utilities
from .logger import setup_logger, get_logger

# Configuration
from .config import get_config, Config

# Browser automation
from .browser import get_stealth_context, safe_goto, auto_scroll, handle_popups

# Data extraction utilities
from .utils import (
    clean_price,
    extract_text,
    extract_attr,
    sanitize_filename,
    extract_number,
    normalize_whitespace,
    truncate_text,
    is_valid_url,
)

# Data validation
from .validators import (
    validate_url,
    sanitize_text,
    validate_product_data,
    validate_job_data,
    validate_news_data,
    validate_realestate_data,
    filter_valid_data,
)

__all__ = [
    # Logger
    "setup_logger",
    "get_logger",
    # Config
    "get_config",
    "Config",
    # Browser
    "get_stealth_context",
    "safe_goto",
    "auto_scroll",
    "handle_popups",
    # Utils
    "clean_price",
    "extract_text",
    "extract_attr",
    "sanitize_filename",
    "extract_number",
    "normalize_whitespace",
    "truncate_text",
    "is_valid_url",
    # Validators
    "validate_url",
    "sanitize_text",
    "validate_product_data",
    "validate_job_data",
    "validate_news_data",
    "validate_realestate_data",
    "filter_valid_data",
]
