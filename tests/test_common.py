"""Test suite for common utilities."""

import pytest
from src.common.utils import (
    clean_price,
    extract_number,
    is_valid_url,
    normalize_whitespace,
    sanitize_filename,
    truncate_text,
)


class TestCleanPrice:
    """Tests for clean_price function."""

    def test_clean_price_with_rupee_symbol(self):
        assert clean_price("₹1,234") == 1234

    def test_clean_price_with_dollar(self):
        assert clean_price("$99.99") == 9999

    def test_clean_price_with_text(self):
        assert clean_price("Price: 1,500") == 1500

    def test_clean_price_none(self):
        assert clean_price(None) is None

    def test_clean_price_empty(self):
        assert clean_price("") is None


class TestExtractNumber:
    """Tests for extract_number function."""

    def test_extract_number_reviews(self):
        assert extract_number("123 reviews") == 123

    def test_extract_number_decimal(self):
        assert extract_number("Rating: 4.5 stars") == 4

    def test_extract_number_none(self):
        assert extract_number(None) is None

    def test_extract_number_no_digits(self):
        assert extract_number("no numbers here") is None


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_sanitize_filename_basic(self):
        result = sanitize_filename("Test File: Name/Path")
        # Forward slashes are removed entirely, not replaced
        assert result == "test_file_namepath"

    def test_sanitize_filename_special_chars(self):
        result = sanitize_filename("File@#$%^with&*()special!chars")
        assert "special" in result
        assert "@" not in result

    def test_sanitize_filename_max_length(self):
        long_name = "a" * 300
        result = sanitize_filename(long_name, max_length=50)
        assert len(result) <= 50


class TestNormalizeWhitespace:
    """Tests for normalize_whitespace function."""

    def test_normalize_multiple_spaces(self):
        assert normalize_whitespace("Multiple    spaces   here") == "Multiple spaces here"

    def test_normalize_tabs_and_newlines(self):
        assert normalize_whitespace("Text\t\twith\nnewlines") == "Text with newlines"

    def test_normalize_none(self):
        assert normalize_whitespace(None) is None


class TestTruncateText:
    """Tests for truncate_text function."""

    def test_truncate_long_text(self):
        result = truncate_text("Very long text here", max_length=10)
        assert result == "Very lo..."
        assert len(result) == 10

    def test_truncate_short_text(self):
        result = truncate_text("Short", max_length=10)
        assert result == "Short"

    def test_truncate_custom_suffix(self):
        # Text longer than max_length will be truncated with custom suffix
        result = truncate_text("Very long text here", max_length=10, suffix="--")
        assert result.endswith("--")
        assert len(result) == 10


class TestIsValidUrl:
    """Tests for is_valid_url function."""

    def test_valid_https_url(self):
        assert is_valid_url("https://example.com") is True

    def test_valid_http_url(self):
        assert is_valid_url("http://example.com") is True

    def test_valid_url_with_path(self):
        assert is_valid_url("https://example.com/path/to/page") is True

    def test_invalid_url(self):
        assert is_valid_url("not a url") is False

    def test_valid_localhost(self):
        assert is_valid_url("http://localhost:8000") is True

    def test_none_url(self):
        assert is_valid_url(None) is False
