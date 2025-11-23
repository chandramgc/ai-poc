#!/usr/bin/env python3
"""
Verification script to check project installation and configuration.
Run this after setup to ensure everything is working correctly.
"""
import sys
import subprocess
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    try:
        subprocess.run(
            ["which", command],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(command: list, description: str) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description}")
            print(f"   Error: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {str(e)[:100]}")
        return False


def main():
    """Run verification checks."""
    print_header("Medicine News Scraper - Installation Verification")
    
    all_checks_passed = True
    
    # Check 1: Required files exist
    print_header("1. Checking Required Files")
    required_files = [
        "pyproject.toml",
        "app/main.py",
        "app/api/routes.py",
        "app/core/config.py",
        "app/core/cache.py",
        "app/models/article.py",
        "app/scraper/google_search.py",
        "tests/test_scraper.py",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
    ]
    
    for filepath in required_files:
        if check_file_exists(filepath):
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath} - MISSING")
            all_checks_passed = False
    
    # Check 2: Poetry installed
    print_header("2. Checking Poetry Installation")
    if check_command_exists("poetry"):
        print("✅ Poetry is installed")
        
        # Check Poetry version
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                text=True
            )
            print(f"   Version: {result.stdout.strip()}")
        except Exception as e:
            print(f"   Warning: Could not get Poetry version: {e}")
    else:
        print("❌ Poetry is NOT installed")
        print("   Install with: curl -sSL https://install.python-poetry.org | python3 -")
        all_checks_passed = False
    
    # Check 3: Python version
    print_header("3. Checking Python Version")
    python_version = sys.version_info
    if python_version >= (3, 9):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        print("   Required: Python 3.9 or higher")
        all_checks_passed = False
    
    # Check 4: Dependencies installed
    print_header("4. Checking Dependencies")
    try:
        import fastapi
        print(f"✅ fastapi installed (version {fastapi.__version__})")
    except ImportError:
        print("❌ fastapi not installed")
        print("   Run: poetry install")
        all_checks_passed = False
    
    try:
        import uvicorn
        print(f"✅ uvicorn installed (version {uvicorn.__version__})")
    except ImportError:
        print("❌ uvicorn not installed")
        print("   Run: poetry install")
        all_checks_passed = False
    
    try:
        import pydantic
        print(f"✅ pydantic installed (version {pydantic.__version__})")
    except ImportError:
        print("❌ pydantic not installed")
        print("   Run: poetry install")
        all_checks_passed = False
    
    try:
        import requests
        print(f"✅ requests installed (version {requests.__version__})")
    except ImportError:
        print("❌ requests not installed")
        print("   Run: poetry install")
        all_checks_passed = False
    
    try:
        import bs4
        print(f"✅ beautifulsoup4 installed (version {bs4.__version__})")
    except ImportError:
        print("❌ beautifulsoup4 not installed")
        print("   Run: poetry install")
        all_checks_passed = False
    
    # Check 5: Environment configuration
    print_header("5. Checking Environment Configuration")
    if check_file_exists(".env"):
        print("✅ .env file exists")
    elif check_file_exists(".env.example"):
        print("⚠️  .env file not found (using defaults)")
        print("   Consider: cp .env.example .env")
    else:
        print("❌ Neither .env nor .env.example found")
        all_checks_passed = False
    
    # Check 6: Docker (optional)
    print_header("6. Checking Docker (Optional)")
    if check_command_exists("docker"):
        print("✅ Docker is installed")
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            print(f"   Version: {result.stdout.strip()}")
        except Exception:
            pass
    else:
        print("ℹ️  Docker not installed (optional)")
    
    if check_command_exists("docker-compose"):
        print("✅ Docker Compose is installed")
    else:
        print("ℹ️  Docker Compose not installed (optional)")
    
    # Check 7: Run basic import test
    print_header("7. Testing Application Imports")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from app.main import app
        print("✅ Application imports successfully")
    except Exception as e:
        print(f"❌ Application import failed: {str(e)[:100]}")
        all_checks_passed = False
    
    # Final summary
    print_header("Verification Summary")
    if all_checks_passed:
        print("✅ All checks passed! The project is ready to use.")
        print("\nNext steps:")
        print("  1. Run tests: poetry run pytest")
        print("  2. Start server: poetry run uvicorn app.main:app --reload")
        print("  3. Open docs: http://localhost:8000/docs")
        print("\nOr use Make commands:")
        print("  make test")
        print("  make dev")
        return 0
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("  - Install Poetry: curl -sSL https://install.python-poetry.org | python3 -")
        print("  - Install dependencies: poetry install")
        print("  - Create .env: cp .env.example .env")
        return 1


if __name__ == "__main__":
    sys.exit(main())
