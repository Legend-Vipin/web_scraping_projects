"""Data validation utilities for scraped data."""

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


def validate_url(url: Optional[str]) -> bool:
    """
    Validate if a string is a properly formatted URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise
    """
    if not url:
        return False

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_text(text: Optional[str]) -> Optional[str]:
    """
    Sanitize text by removing null bytes, excessive whitespace, and control characters.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text or None
    """
    if not text:
        return None

    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove control characters except newline and tab
    text = "".join(char for char in text if ord(char) >= 32 or char in "\n\t")

    # Normalize whitespace
    text = " ".join(text.split())

    return text.strip() if text.strip() else None


def validate_product_data(data: Dict[str, Any]) -> bool:
    """
    Validate product data structure.

    Args:
        data: Product data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["platform", "title", "url"]

    # Check required fields exist
    if not all(field in data for field in required_fields):
        return False

    # Validate title is not empty
    if not data.get("title"):
        return False

    # Validate URL format
    if not validate_url(data.get("url")):
        return False

    return True


def validate_job_data(data: Dict[str, Any]) -> bool:
    """
    Validate job listing data structure.

    Args:
        data: Job data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["title", "company"]

    # Check required fields exist and are not empty
    if not all(data.get(field) for field in required_fields):
        return False

    return True


def validate_news_data(data: Dict[str, Any]) -> bool:
    """
    Validate news headline data structure.

    Args:
        data: News data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["source", "headline", "link"]

    # Check required fields exist
    if not all(field in data for field in required_fields):
        return False

    # Validate headline is not empty
    if not data.get("headline"):
        return False

    # Validate link is a valid URL
    if not validate_url(data.get("link")):
        return False

    return True


def validate_realestate_data(data: Dict[str, Any]) -> bool:
    """
    Validate real estate property data structure.

    Args:
        data: Property data dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["title", "location"]

    # Check required fields exist and are not empty
    if not all(data.get(field) for field in required_fields):
        return False

    return True


def filter_valid_data(
    data_list: List[Dict[str, Any]], validator_func: callable
) -> List[Dict[str, Any]]:
    """
    Filter a list of data dictionaries, keeping only valid entries.

    Args:
        data_list: List of data dictionaries
        validator_func: Validation function to apply

    Returns:
        List of valid data dictionaries
    """
    valid_data = []

    for item in data_list:
        # Sanitize text fields
        for key, value in item.items():
            if isinstance(value, str):
                item[key] = sanitize_text(value)

        # Validate and keep if valid
        if validator_func(item):
            valid_data.append(item)

    return valid_data
