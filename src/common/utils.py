"""Common utility functions for data extraction and processing."""

import re
from typing import List, Optional

from bs4 import Tag


def clean_price(price_raw: Optional[str]) -> Optional[int]:
    """
    Extract numeric price from a string containing currency symbols and formatting.

    Args:
        price_raw: Raw price string (e.g., "₹1,234.56", "$99.99")

    Returns:
        Integer price value or None if extraction fails

    Examples:
        >>> clean_price("₹1,234")
        1234
        >>> clean_price("$99.99")
        99
        >>> clean_price("Price: 1,500")
        1500
    """
    if not price_raw:
        return None

    try:
        # Remove all non-digit characters
        clean = "".join(filter(str.isdigit, price_raw))
        return int(clean) if clean else None
    except (ValueError, TypeError):
        return None


def extract_text(
    element: Tag, selectors: List[str], default: Optional[str] = None, strip: bool = True
) -> Optional[str]:
    """
    Try multiple CSS selectors and return the first match's text.

    Args:
        element: BeautifulSoup element to search within
        selectors: List of CSS selectors to try in order
        default: Default value if no selector matches
        strip: Whether to strip whitespace from result

    Returns:
        Extracted text or default value

    Examples:
        >>> soup = BeautifulSoup('<div><h1>Title</h1></div>', 'lxml')
        >>> extract_text(soup, ['h1', 'h2'])
        'Title'
    """
    for selector in selectors:
        try:
            found = element.select_one(selector)
            if found:
                text = found.get_text(strip=strip)
                if text:
                    return text
        except Exception:
            continue

    return default


def extract_attr(
    element: Tag, selectors: List[str], attr: str, default: Optional[str] = None
) -> Optional[str]:
    """
    Try multiple CSS selectors and return the first match's attribute value.

    Args:
        element: BeautifulSoup element to search within
        selectors: List of CSS selectors to try in order
        attr: Attribute name to extract
        default: Default value if no selector matches

    Returns:
        Extracted attribute value or default value

    Examples:
        >>> soup = BeautifulSoup('<a href="/page">Link</a>', 'lxml')
        >>> extract_attr(soup, ['a'], 'href')
        '/page'
    """
    for selector in selectors:
        try:
            found = element.select_one(selector)
            if found and found.has_attr(attr):
                value = found[attr]
                if value:
                    return value
        except Exception:
            continue

    return default


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize a string to be used as a safe filename.

    Args:
        filename: Original filename string
        max_length: Maximum length of resulting filename

    Returns:
        Sanitized filename string

    Examples:
        >>> sanitize_filename("Test File: Name/Path")
        'test_file_name_path'
    """
    # Replace spaces and special characters with underscores
    safe = re.sub(r"[^\w\s-]", "", filename.lower())
    safe = re.sub(r"[-\s]+", "_", safe)

    # Truncate if too long
    if len(safe) > max_length:
        safe = safe[:max_length]

    return safe.strip("_")


def extract_number(text: Optional[str]) -> Optional[int]:
    """
    Extract the first number from a text string.

    Args:
        text: Input text containing numbers

    Returns:
        First number found or None

    Examples:
        >>> extract_number("123 reviews")
        123
        >>> extract_number("Rating: 4.5 stars")
        4
    """
    if not text:
        return None

    try:
        # Find first sequence of digits
        match = re.search(r"\d+", text)
        if match:
            return int(match.group())
    except (ValueError, AttributeError):
        pass

    return None


def normalize_whitespace(text: Optional[str]) -> Optional[str]:
    """
    Normalize whitespace in text (replace multiple spaces with single space).

    Args:
        text: Input text

    Returns:
        Text with normalized whitespace

    Examples:
        >>> normalize_whitespace("Multiple    spaces   here")
        'Multiple spaces here'
    """
    if not text:
        return None

    return " ".join(text.split())


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with optional suffix.

    Args:
        text: Input text
        max_length: Maximum length including suffix
        suffix: Suffix to append if truncated

    Returns:
        Truncated text

    Examples:
        >>> truncate_text("Very long text here", max_length=10)
        'Very lo...'
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def is_valid_url(url: Optional[str]) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid URL, False otherwise

    Examples:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("not a url")
        False
    """
    if not url:
        return False

    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return bool(url_pattern.match(url))
