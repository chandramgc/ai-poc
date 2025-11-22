#!/bin/bash
# Installation and Setup Verification Script
# Run this after initial setup to verify everything is configured correctly

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================"
echo "LLM FastAPI Service - Verification"
echo "================================"
echo ""

# Track success/failure
SUCCESS=0
FAILURES=0

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        SUCCESS=$((SUCCESS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        SUCCESS=$((SUCCESS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $1 not found"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        SUCCESS=$((SUCCESS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $1 directory not found"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

check_env_var() {
    if [ -f .env ] && grep -q "^$1=" .env; then
        VALUE=$(grep "^$1=" .env | cut -d '=' -f2-)
        if [ -n "$VALUE" ] && [ "$VALUE" != "your_token_here" ] && [ "$VALUE" != "your-api-key-here" ]; then
            echo -e "${GREEN}✓${NC} $1 is set in .env"
            SUCCESS=$((SUCCESS + 1))
            return 0
        else
            echo -e "${YELLOW}⚠${NC} $1 is in .env but needs a value"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} $1 not found in .env"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# 1. Check required commands
echo -e "\n${YELLOW}Checking required commands...${NC}"
check_command python3
check_command poetry
check_command curl
check_command docker || echo -e "${YELLOW}⚠${NC} Docker is optional but recommended"

# 2. Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
REQUIRED_VERSION="3.11"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (>= $REQUIRED_VERSION required)"
    SUCCESS=$((SUCCESS + 1))
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION (>= $REQUIRED_VERSION required)"
    FAILURES=$((FAILURES + 1))
fi

# 3. Check Poetry version
echo -e "\n${YELLOW}Checking Poetry version...${NC}"
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo -e "${GREEN}✓${NC} Poetry $POETRY_VERSION installed"
    SUCCESS=$((SUCCESS + 1))
fi

# 4. Check project structure
echo -e "\n${YELLOW}Checking project structure...${NC}"
check_directory "app"
check_directory "app/api"
check_directory "app/core"
check_directory "app/llm"
check_directory "tests"

# 5. Check key files
echo -e "\n${YELLOW}Checking key files...${NC}"
check_file "pyproject.toml"
check_file "config.yml"
check_file ".env.example"
check_file "Dockerfile"
check_file "Makefile"
check_file "README.md"

# 6. Check if .env exists and is configured
echo -e "\n${YELLOW}Checking .env configuration...${NC}"
if check_file ".env"; then
    check_env_var "HUGGINGFACE_TOKEN"
    check_env_var "SECURITY__API_KEY"
else
    echo -e "${YELLOW}⚠${NC} Run: cp .env.example .env and configure it"
fi

# 7. Check Poetry dependencies
echo -e "\n${YELLOW}Checking Poetry installation...${NC}"
if [ -d ".venv" ] || poetry env info &> /dev/null; then
    echo -e "${GREEN}✓${NC} Poetry virtual environment exists"
    SUCCESS=$((SUCCESS + 1))
    
    # Check if dependencies are installed
    if poetry run python -c "import fastapi" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Dependencies appear to be installed"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -e "${RED}✗${NC} Dependencies not installed. Run: poetry install"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${RED}✗${NC} Virtual environment not found. Run: poetry install"
    FAILURES=$((FAILURES + 1))
fi

# 8. Check application files
echo -e "\n${YELLOW}Checking application modules...${NC}"
check_file "app/main.py"
check_file "app/core/config.py"
check_file "app/llm/loader.py"
check_file "app/api/routers/inference.py"
check_file "app/api/routers/chat.py"

# 9. Check if service can import
echo -e "\n${YELLOW}Checking if application imports successfully...${NC}"
if [ -d ".venv" ] || poetry env info &> /dev/null; then
    if poetry run python -c "from app.main import app; print('OK')" 2>/dev/null | grep -q "OK"; then
        echo -e "${GREEN}✓${NC} Application imports successfully"
        SUCCESS=$((SUCCESS + 1))
    else
        echo -e "${RED}✗${NC} Application import failed"
        FAILURES=$((FAILURES + 1))
        echo "Try running: poetry install"
    fi
fi

# 10. Summary
echo ""
echo "================================"
echo "Verification Summary"
echo "================================"
echo -e "${GREEN}Success:${NC} $SUCCESS checks passed"
echo -e "${RED}Failures:${NC} $FAILURES checks failed"
echo ""

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! You're ready to start.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Ensure .env is configured with your tokens"
    echo "  2. Run: make run"
    echo "  3. Test: curl http://localhost:8000/health"
    echo "  4. See: ./examples.sh for more examples"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Run: poetry install"
    echo "  - Run: cp .env.example .env (then edit it)"
    echo "  - Install Python 3.11+: https://www.python.org/downloads/"
    echo "  - Install Poetry: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi
