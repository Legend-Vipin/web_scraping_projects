# 🕸️ Web Scraping Projects

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![uv](https://img.shields.io/badge/uv-enabled-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A collection of professional, production-grade web scraping tools built with Python 3.11+. This repository demonstrates best practices in web scraping, including robust error handling, anti-detection techniques, modular architecture, and structured data extraction.

---

## ✨ Features

- **Modular Architecture**: Clean `src/` layout with separate modules for E-commerce, Jobs, News, and Real Estate
- **Common Utilities**: Shared logging, browser automation, and data processing utilities
- **Modern Tooling**: Built with `uv` for lightning-fast dependency management (pip compatible)
- **Anti-Detection**: Stealth browser configurations and randomized behaviors
- **Robust Logging**: Rotating file handlers with color-coded console output
- **Cross-Platform**: Full support for Windows, macOS, and Linux
- **Data Export**: Automatically saves data in CSV and JSON formats

---

## 📁 Project Structure

```
web_scraping_projects/
├── src/                      # Source code directory
│   ├── common/              # Shared utilities
│   │   ├── logger.py        # Centralized logging
│   │   ├── browser.py       # Browser automation helpers
│   │   └── utils.py         # Data processing utilities
│   ├── ecommerce/           # E-commerce price tracker (Amazon/Flipkart)
│   │   └── tracker.py
│   ├── jobs/                # Job portal scraper (Naukri)
│   │   └── scraper.py
│   ├── news/                # News aggregator (TOI/Hindu/NDTV)
│   │   └── aggregator.py
│   └── realestate/          # Real estate crawler (99acres)
│       └── crawler.py
├── data/                    # Output data files (CSV/JSON)
├── logs/                    # Log files with rotation
├── config/                  # Configuration files
│   └── .env.example        # Environment variable template
├── tests/                   # Test directory
├── pyproject.toml          # Modern Python packaging config
├── requirements.txt         # Consolidated dependencies
├── Makefile                 # Helpful commands
├── setup.sh                 # Automated setup script
└── README.md

```

---

## 🚀 Quick Start

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/Legend-Vipin/web_scraping_projects
cd web_scraping_projects

# Run automated setup (creates venv, installs dependencies)
./setup.sh
```

### Manual Setup

If you prefer manual control:

```bash
# Create virtual environment
make install

# Install Playwright browsers
make browsers

# View all available commands
make help
```

---

## 🛠️ Requirements

- **Python 3.11+**
- **uv** (Recommended for faster installs) or **pip**
- **Git**

### Installing uv (Optional but Recommended)

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Homebrew (macOS):**
```bash
brew install uv
```

---

## 💻 Usage

### Running Scrapers

Activate the virtual environment first:
```bash
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

Then run any scraper using make commands:

```bash
# E-commerce Price Tracker (Amazon + Flipkart)
make run-ecommerce
# Options: --query "laptops" --pages 3 --headless

# Job Portal Scraper (Naukri)
make run-job
# Options: --role "python developer" --location "remote"

# News Headline Aggregator (TOI, Hindu, NDTV)
make run-news
# No options needed

# Real Estate Crawler (99acres)
make run-real
# Options: --city "pune"
```

### Custom Arguments

Run scrapers directly with custom arguments:

```bash
# E-commerce with custom search
python src/ecommerce/tracker.py --query "gaming laptops" --pages 5 --no-headless

# Jobs with specific criteria
python src/jobs/scraper.py --role "data scientist" --location "bangalore"

# Real estate for specific city
python src/realestate/crawler.py --city "mumbai"
```

---

## 📊 Output

### Data Files
All scraped data is saved to the `data/` directory:

```
data/
├── gaming_laptops_20260120_163000.csv
├── gaming_laptops_20260120_163000.json
├── jobs_20260120_163500.csv
├── headlines_20260120_163559.csv
└── realestate_20260120_164000.csv
```

### Log Files
Detailed logs are saved to the `logs/` directory with automatic rotation:

```
logs/
├── ecommerce_tracker.log      # Current log
├── ecommerce_tracker.log.1    # Backup 1 (10MB max each)
├── job_scraper.log
├── news_aggregator.log
└── realestate_crawler.log
```

---

## ⚙️ Configuration

Copy the example environment file and customize:

```bash
cp config/.env.example config/.env
nano config/.env  # Edit your settings
```

Available settings:
- `HEADLESS` - Run browsers in headless mode (true/false)
- `MAX_PAGES` - Maximum pages to scrape per session
- `REQUEST_TIMEOUT` - Request timeout in seconds
- `BLOCK_IMAGES` - Block images for faster scraping
- And more...

---

## 🧰 Development

### Available Make Commands

Run `make help` to see all commands:

```
make install         # Create venv & install dependencies
make browsers        # Install Playwright browsers
make run-ecommerce   # Run e-commerce tracker
make run-job         # Run job scraper
make run-news        # Run news aggregator
make run-real        # Run real estate crawler
make clean           # Remove generated files
make clean-all       # Remove venv too
make format          # Format code with black
make lint            # Lint code with ruff
make help            # Show all commands
```

### Code Quality Tools

Install development dependencies:
```bash
pip install '.[dev]'  # Includes: pytest, black, ruff, mypy
```

Then use:
```bash
make format   # Auto-format code
make lint     # Check code quality
```

---

## 📝 Troubleshooting

### Common Issues

**"Module not found" error**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
```

**"Permission denied" on setup.sh**
```bash
chmod +x setup.sh
./setup.sh
```

**Playwright browsers not installed**
```bash
make browsers
# or
python -m playwright install
```

**CAPTCHA detected**
- Increase delays between requests
- Use `--no-headless` to see what's happening
- Check if site has rate limiting

**No data collected**
- Website structure may have changed
- Check logs in `logs/` directory for errors
- Try with `--no-headless` to debug visually

---

## 🏗️ Architecture

### Common Utilities

The `src/common/` module provides reusable components:

- **logger.py**: Centralized logging with color output and file rotation
- **browser.py**: Anti-detection browser setup, safe navigation, auto-scrolling
- **utils.py**: Data extraction helpers, price cleaning, text processing

### Scraper Modules

Each scraper in `src/` follows a consistent pattern:
1. Import common utilities
2. Define scraper class
3. Implement extraction logic
4. Save results to `data/` directory
5. Log activities to `logs/` directory

---

## 🔒 Best Practices

### Security
- Never commit `.env` files or API keys
- Use environment variables for sensitive data
- Review `.gitignore` to ensure proper exclusions

### Performance
- Use `uv` for 10-100x faster dependency installs
- Enable image blocking for faster page loads
- Implement appropriate delays to avoid rate limiting

### Scraping Ethics
- Respect `robots.txt` files
- Don't overwhelm servers with requests
- Add delays between requests
- Use data responsibly

---

## 📚 Project Specifics

### E-commerce Tracker
- **Sites**: Amazon India, Flipkart
- **Data**: Product title, price, rating, reviews, availability
- **Pagination**: Supports multiple pages

### Job Scraper
- **Sites**: Naukri.com
- **Data**: Job title, company, experience, salary, location
- **Custom**: Search by role and location

### News Aggregator
- **Sites**: Times of India, The Hindu, NDTV
- **Data**: Headlines, links, timestamps
- **Concurrent**: Scrapes all sites simultaneously

### Real Estate Crawler
- **Sites**: 99acres.com
- **Data**: Property title, price, location, link
- **Custom**: Search by city

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact

**Author**: Legend-Vipin  
**Repository**: [web_scraping_projects](https://github.com/Legend-Vipin/web_scraping_projects)

---

## ⭐ Acknowledgments

- [Playwright](https://playwright.dev/) - Browser automation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Pandas](https://pandas.pydata.org/) - Data processing
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
