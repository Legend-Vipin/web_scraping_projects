"""Common utilities for web scraping projects."""

# Logger utilities
# Browser automation
from .browser import auto_scroll, get_stealth_context, handle_popups, safe_goto

# Configuration
from .config import Config, get_config
from .logger import get_logger, setup_logger

# Data extraction utilities
from .utils import (
    clean_price,
    extract_attr,
    extract_number,
    extract_text,
    is_valid_url,
    normalize_whitespace,
    sanitize_filename,
    truncate_text,
)

# Data validation
from .validators import (
    filter_valid_data,
    sanitize_text,
    validate_job_data,
    validate_news_data,
    validate_product_data,
    validate_realestate_data,
    validate_url,
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
