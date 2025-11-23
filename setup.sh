#!/bin/bash

# Medicine News Scraper - Setup Script
# This script helps set up the project for first-time use

set -e  # Exit on error

echo "🚀 Medicine News Scraper - Setup Script"
echo "========================================"
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ Poetry installed successfully"
else
    echo "✅ Poetry is already installed"
fi

echo ""
echo "📥 Installing project dependencies..."
poetry install

echo ""
echo "📋 Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created. Please review and customize if needed."
else
    echo "ℹ️  .env file already exists. Skipping."
fi

echo ""
echo "🧪 Running tests to verify setup..."
poetry run pytest -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review and customize .env file if needed"
echo "  2. Start the development server: make dev"
echo "  3. Open API docs: http://localhost:8000/docs"
echo "  4. Try a search: make search"
echo ""
echo "For more information, see:"
echo "  - QUICKSTART.md for quick start guide"
echo "  - README.md for complete documentation"
echo "  - PROJECT_SUMMARY.md for project overview"
echo ""
echo "Happy scraping! 🔍"
