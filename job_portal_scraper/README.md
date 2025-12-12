# Job Portal Scraper

Scrapes Naukri.com for job listings.

## Features
- **Job Extraction**: Title, Company, Experience, Salary, Location.
- **Export**: CSV/JSON.
- **Stealth**: Uses Playwright with stealth techniques.

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
    uv run scraper.py --role "Python Developer" --location "Remote"
    ```
