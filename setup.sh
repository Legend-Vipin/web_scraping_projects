#!/usr/bin/env bash
# ============================================================================
# Web Scraping Projects - Setup Script
# ============================================================================
# Creates virtual environment, installs dependencies, and sets up project

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
VENV_DIR="$ROOT_DIR/.venv"

echo "=========================================="
echo "Web Scraping Projects - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "✗ Python 3 is required but not found"
    exit 1
fi

# Ensure required directories exist
echo ""
echo "Creating project directories..."
mkdir -p "$ROOT_DIR"/{data,logs,config}
echo "✓ Directories created: data/, logs/, config/"

# Check for uv and create virtual environment
echo ""
if command -v uv >/dev/null 2>&1; then
    echo "✓ Detected 'uv' — using uv for fast dependency management"
    echo "Creating virtual environment with uv..."
    uv venv
    
    echo "Installing dependencies..."
    uv pip install --upgrade pip setuptools wheel
    uv pip install -r "$ROOT_DIR/requirements.txt"
    
    echo ""
    echo "Installing Playwright browsers..."
    uv run python -m playwright install || {
        echo "⚠ Playwright browser installation failed (non-critical)"
    }
else
    echo "⚠ 'uv' not found — falling back to standard python3 venv + pip"
    echo "  Tip: Install uv for faster dependency management:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    echo "Installing dependencies..."
    "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
    "$VENV_DIR/bin/pip" install -r "$ROOT_DIR/requirements.txt"
    
    echo ""
    echo "Installing Playwright browsers..."
    "$VENV_DIR/bin/python" -m playwright install || {
        echo "⚠ Playwright browser installation failed (non-critical)"
    }
fi

# Check if .env exists
echo ""
if [ ! -f "$ROOT_DIR/config/.env" ]; then
    echo "⚠ No .env file found"
    echo "  Creating from template..."
    cp "$ROOT_DIR/config/.env.example" "$ROOT_DIR/config/.env" 2>/dev/null || true
    echo "  Edit config/.env to customize settings"
fi

# Display completion message
echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate the environment:"
if command -v uv >/dev/null 2>&1; then
    echo "     source .venv/bin/activate"
    echo "     (or use 'uv run' prefix for commands)"
else
    echo "     source .venv/bin/activate"
fi
echo ""
echo "  2. Run a scraper:"
echo "     make run-ecommerce  # E-commerce tracker"
echo "     make run-job        # Job portal scraper"
echo "     make run-news       # News aggregator"
echo "     make run-real       # Real estate crawler"
echo ""
echo "  3. View all available commands:"
echo "     make help"
echo ""
