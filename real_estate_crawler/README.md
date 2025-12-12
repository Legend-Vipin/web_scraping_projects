# Real Estate Crawler

Crawls 99acres for properties.

## Features
- **Property Data**: Price, Name, Location.
- **Stealth**: Uses Playwright Stealth.

## Setup

1.  **Install dependencies**:
    ```bash
    uv venv --python 3.11
    source .venv/bin/activate
    uv pip install -r requirements.txt
    uv run playwright install chromium
    ```

2.  **Run**:
    ```bash
    uv run crawler.py --city "Pune"
    ```
