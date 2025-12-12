# News Headline Aggregator

Aggregates headlines from key Indian news sites: TOI, The Hindu, NDTV.

## Features
- **Fast Scraper**: Uses `httpx` for async HTTP requests (no browser needed).
- **Consolidation**: Merges headlines into a single CSV/JSON.

## Setup

1.  **Install dependencies**:
    ```bash
    uv venv --python 3.11
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

2.  **Run**:
    ```bash
    uv run aggregator.py
    ```
