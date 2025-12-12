# Ecommerce Price Tracker

A production-grade, multipage asynchronous web scraper for Amazon.in and Flipkart.com using Python and Playwright.

## Features
1.  **Install dependencies**:
    ```bash
    uv venv --python 3.11
    source .venv/bin/activate
    uv pip install -r requirements.txt
    uv run playwright install chromium
    ```

2.  **Run**:
    ```bash
    uv run tracker.py --query "gaming laptop"
    ```
