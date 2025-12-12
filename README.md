# 🕸️ Web Scraping Projects

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![uv](https://img.shields.io/badge/uv-enabled-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A collection of professional, production-grade web scraping tools built with Python 3.11. This repository demonstrates best practices in web scraping, including robust error handling, anti-detection techniques, and structured data extraction.

---

## ✨ Features

*   **Modular Architecture**: Separate projects for E-commerce, Job Portals, News Aggregation, and Real Estate.
*   **Modern Tooling**: Built with `uv` for lightning-fast dependency management (compatible with `pip`).
*   **Cross-Platform**: Full support for Windows, macOS, and Linux (including Kali/Arch).
*   **Robust Logging**: Detailed logs for every operation to aid debugging.
*   **Data Export**: Automatically saves data in CSV and JSON formats.

---

## � Folder Structure

```tree
web_scraping_projects/
├── ecommerce_price_tracker/    # Tracks product prices on Amazon/Flipkart
│   ├── tracker.py
│   ├── requirements.txt
│   └── tracker.log
├── job_portal_scraper/         # Scrapes job listings
│   ├── scraper.py
│   ├── requirements.txt
│   └── scraper.log
├── news_headline_aggregator/   # Aggregates news headlines
│   ├── aggregator.py
│   ├── requirements.txt
│   └── aggregator.log
├── real_estate_crawler/        # Crawls real estate listings
│   ├── crawler.py
│   ├── requirements.txt
│   └── crawler.log
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🛠️ Requirements

*   **Python 3.11+**
*   **uv** (Recommended) or **pip**
*   **Git**

---

## 📥 Installation

### 🪟 Windows

1.  **Install Python**:
    Download and install Python 3.11+ from the [official website](https://www.python.org/downloads/) or via `uv` (see below). Ensure you check **"Add Python to PATH"**.

2.  **Install `uv` (PowerShell)**:
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

3.  **Clone the Repository**:
    ```powershell
    git clone <your-repo-url>
    cd web_scraping_projects
    ```

### 🍎 macOS

1.  **Install Homebrew** (if not installed):
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2.  **Install Python & uv**:
    ```bash
    brew install python@3.11 uv
    ```

3.  **Clone the Repository**:
    ```bash
    git clone <your-repo-url>
    cd web_scraping_projects
    ```

### 🐧 Linux (Ubuntu/Debian + Arch + Kali)

#### Ubuntu / Debian / Kali
1.  **Update & Install Basics**:
    ```bash
    sudo apt update && sudo apt install -y python3 python3-pip git curl
    ```
    *(Note for Kali Users: Ensure your repositories are updated. You may need to use `venv` for all pip operations due to PEP 668).*

2.  **Install `uv`**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

#### Arch Linux
1.  **Install Dependencies**:
    ```bash
    sudo pacman -S python python-pip uv git
    ```

---

## ⚙️ Environment Setup

We recommend using **uv** for the fastest and most reliable experience.

### Option A: Using `uv` (Recommended)

1.  **Create Virtual Environment**:
    ```bash
    uv venv
    ```
    *Windows users: This logs strictly to `v` folder by default in some configs, or standard `.venv`.*

2.  **Activate Environment**:
    *   **Linux/macOS**: `source .venv/bin/activate`
    *   **Windows**: `.venv\Scripts\activate`

3.  **Install Dependencies**:
    ```bash
    uv pip install -r requirements.txt
    ```
    *Or to sync all dependencies at once if a lockfile existed:*
    ```bash
    uv sync
    ```

### Option B: Using Standard `pip`

1.  **Create Virtual Environment**:
    ```bash
    python3 -m venv venv
    ```

2.  **Activate Environment**:
    *   **Linux/macOS**: `source venv/bin/activate`
    *   **Windows**: `venv\Scripts\activate`

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Running the Project

Navigate to the specific project folder you want to run.

**Example: E-commerce Price Tracker**

```bash
cd ecommerce_price_tracker
```

**Using `uv`:**
```bash
uv run tracker.py
```

**Using Standard Python:**
```bash
# Ensure venv is active
python tracker.py
```

---

## 📦 Updating Dependencies

**With `uv`:**
```bash
uv pip compile requirements.in -o requirements.txt  # If using .in files
# Or simply update installed packages
uv pip install -U -r requirements.txt
```

**With `pip`:**
```bash
pip install -U -r requirements.txt
```

---

## 📝 Logs & Troubleshooting

### Logs Location
Each sub-project writes logs to its own directory:
*   `ecommerce_price_tracker/tracker.log`
*   `job_portal_scraper/scraper.log`
*   etc.

### Troubleshooting

*   **"Module not found"**: Ensure your virtual environment is activated (`source .venv/bin/activate`).
*   **Permission Denied (Linux/Mac)**: You might need to `chmod +x` scripts or check folder permissions.
*   **Kali Linux**: If `pip` fails with "externally-managed-environment", use a virtual environment (`uv venv` or `python3 -m venv .venv`).

---

## 💡 Recommendations

### Recommended Tools
*   **VS Code Extensions**:
    *   Python (Microsoft)
    *   Pylance
    *   Ruff (for linting)
*   **CLI Tools**:
    *   `jq` (for processing JSON output on CLI)
    *   `httpie` (alternative to curl)

### Security Notes
*   Never commit API keys to GitHub.
*   Use environment variables for sensitive data.

### Performance
*   **Python Version Manager**: `uv` is recommended over `pyenv` and `conda` for speed.
*   **Libraries**: We use standard, high-performance libraries. Consider `aiohttp` or `playwright` for more complex async scraping needs in the future.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
