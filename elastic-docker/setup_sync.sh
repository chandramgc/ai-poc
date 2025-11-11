#!/bin/bash
#
# Quick setup script for PostgreSQL to Elasticsearch sync
#

echo "🔧 Setting up PostgreSQL to Elasticsearch sync environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "📥 Installing required Python packages..."
pip install --quiet --upgrade pip
pip install psycopg2-binary elasticsearch

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Update PostgreSQL password in pg_to_es_sync.py (line 33)"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python3 pg_to_es_sync.py"
echo ""
