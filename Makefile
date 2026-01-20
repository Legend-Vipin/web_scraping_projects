# ============================================================================
# Web Scraping Projects - Makefile
# ============================================================================
# Quick commands to manage the project

.PHONY: venv install browsers clean run-ecommerce run-job run-news run-real run-all scrape format lint test help

# Default target
.DEFAULT_GOAL := help

# ----------------------------------------------------------------------------
# Environment Setup
# ----------------------------------------------------------------------------

venv:  ## Create virtual environment
	@echo "Creating virtual environment..."
	@if command -v uv >/dev/null 2>&1; then \
		uv venv; \
	else \
		python3 -m venv .venv; \
	fi
	@echo "✓ Virtual environment created"

install: venv  ## Install dependencies
	@echo "Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install --upgrade pip setuptools wheel; \
		uv pip install -e ".[dev]"; \
	else \
		.venv/bin/python -m pip install --upgrade pip setuptools wheel; \
		.venv/bin/pip install -e ".[dev]"; \
	fi
	@echo "✓ Dependencies installed"

browsers:  ## Install Playwright browsers
	@echo "Installing Playwright browsers..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run python -m playwright install; \
	else \
		.venv/bin/python -m playwright install; \
	fi
	@echo "✓ Playwright browsers installed"

# ----------------------------------------------------------------------------
# Run Scrapers
# ----------------------------------------------------------------------------

run-ecommerce:  ## Run e-commerce price tracker
	@if command -v uv >/dev/null 2>&1; then \
		uv run python src/ecommerce/tracker.py; \
	else \
		.venv/bin/python src/ecommerce/tracker.py; \
	fi

run-job:  ## Run job portal scraper
	@if command -v uv >/dev/null 2>&1; then \
		uv run python src/jobs/scraper.py; \
	else \
		.venv/bin/python src/jobs/scraper.py; \
	fi

run-news:  ## Run news headline aggregator
	@if command -v uv >/dev/null 2>&1; then \
		uv run python src/news/aggregator.py; \
	else \
		.venv/bin/python src/news/aggregator.py; \
	fi

run-real:  ## Run real estate crawler
	@if command -v uv >/dev/null 2>&1; then \
		uv run python src/realestate/crawler.py; \
	else \
		.venv/bin/python src/realestate/crawler.py; \
	fi

run-all:  ## Run all scrapers sequentially
	@echo "🚀 Running all scrapers..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run python scrape.py all; \
	else \
		.venv/bin/python scrape.py all; \
	fi

scrape:  ## Run master CLI (usage: make scrape ARGS="<command> [options]")
	@if command -v uv >/dev/null 2>&1; then \
		uv run python scrape.py $(ARGS); \
	else \
		.venv/bin/python scrape.py $(ARGS); \
	fi

# ----------------------------------------------------------------------------
# Cleanup
# ----------------------------------------------------------------------------

clean:  ## Remove generated files and caches
	@echo "Cleaning up generated files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -f data/*.csv data/*.json 2>/dev/null || true
	@rm -f logs/*.log logs/*.log.* 2>/dev/null || true
	@echo "✓ Cleanup complete"

clean-all: clean  ## Remove everything including virtual environment
	@echo "Removing virtual environment..."
	@rm -rf .venv 2>/dev/null || true
	@echo "✓ Complete cleanup done"

# ----------------------------------------------------------------------------
# Development Tools
# ----------------------------------------------------------------------------

format:  ## Format code with black (requires dev dependencies)
	@if command -v black >/dev/null 2>&1; then \
		black src/ --line-length 100; \
		echo "✓ Code formatted"; \
	else \
		echo "black not installed. Install with: pip install black"; \
		exit 1; \
	fi

lint:  ## Lint code with ruff (requires dev dependencies)
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check src/; \
		echo "✓ Linting complete"; \
	else \
		echo "ruff not installed. Install with: pip install ruff"; \
		exit 1; \
	fi

test:  ## Run tests
	@echo "Running tests..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run pytest -v; \
	else \
		.venv/bin/python -m pytest -v; \
	fi

# ----------------------------------------------------------------------------
# Help
# ----------------------------------------------------------------------------

help:  ## Show this help message
	@echo "Web Scraping Projects - Available Commands"
	@echo "==========================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
