#!/bin/bash

# Web Content Analyzer - Setup Script
# This script initializes a clean environment with all dependencies

set -e  # Exit on any error

echo "🚀 Web Content Analyzer - Environment Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "pyproject.toml not found. Please run this script from the web-content-analyzer directory."
    exit 1
fi

print_info "Setting up Web Content Analyzer environment..."

# Step 1: Check if uv is installed
echo ""
echo "Step 1: Checking uv installation..."
if ! command -v uv &> /dev/null; then
    print_warning "uv not found. Installing uv..."

    # Install uv using the official installer
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    # Check if installation worked
    if command -v uv &> /dev/null; then
        print_status "uv installed successfully"
    else
        print_error "Failed to install uv. Please install manually: https://docs.astral.sh/uv/"
        exit 1
    fi
else
    UV_VERSION=$(uv --version)
    print_status "uv is already installed: $UV_VERSION"
fi

# Step 2: Check Python version
echo ""
echo "Step 2: Checking Python version..."
PYTHON_VERSION=$(uv run python --version 2>/dev/null || echo "Not available")
if [[ "$PYTHON_VERSION" == *"Python 3.1"* ]]; then
    print_status "Python version: $PYTHON_VERSION"
else
    print_info "Python 3.12+ will be installed automatically by uv"
fi

# Step 3: Install project dependencies
echo ""
echo "Step 3: Installing project dependencies..."
print_info "This may take a few minutes on first run..."

uv sync

print_status "Project dependencies installed successfully"

# Step 4: Install Playwright browsers
echo ""
echo "Step 4: Installing Playwright browsers..."
print_info "Installing Chromium browser for web scraping..."

uv run playwright install chromium

print_status "Playwright browsers installed successfully"

# Step 5: Set up environment configuration
echo ""
echo "Step 5: Setting up environment configuration..."

if [[ ! -f ".env" ]]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_warning "IMPORTANT: Edit .env file and add your ANTHROPIC_API_KEY"
    print_info "Get your API key from: https://console.anthropic.com/settings/keys"
else
    print_status ".env file already exists"
fi

# Step 6: Verify installation
echo ""
echo "Step 6: Verifying installation..."

# Check if we can import the main modules
if uv run python -c "
import sys
sys.path.insert(0, 'src')
from web_content_analyzer.simple_analyzer import SimpleWebContentAnalyzer
from web_content_analyzer.config import Config
print('✅ All modules imported successfully')
" 2>/dev/null; then
    print_status "Module imports working correctly"
else
    print_error "Module import verification failed"
    exit 1
fi

# Check if the CLI works
if uv run python analyze.py --help > /dev/null 2>&1; then
    print_status "CLI script working correctly"
else
    print_error "CLI script verification failed"
    exit 1
fi

# Step 7: Display usage information
echo ""
echo "🎉 Setup Complete!"
echo "=================="
print_status "Web Content Analyzer is ready to use!"

echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file and add your ANTHROPIC_API_KEY"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Test with a single URL:"
echo "   ${BLUE}export ANTHROPIC_API_KEY=your_key_here${NC}"
echo "   ${BLUE}uv run python analyze.py https://example.com${NC}"
echo ""
echo "3. Test batch processing:"
echo "   ${BLUE}uv run python analyze.py batch examples/urls.txt${NC}"
echo ""
echo "4. Use the uv package directly:"
echo "   ${BLUE}uvx --from . web-analyzer analyze https://example.com${NC}"

echo ""
echo "📖 Documentation:"
echo "- README.md for detailed usage instructions"
echo "- examples/urls.txt for sample input"
echo "- GitHub: https://github.com/eovidiu/web-content-analyzer"

echo ""
echo "🔧 Development commands:"
echo "- ${BLUE}uv sync${NC}                    # Update dependencies"
echo "- ${BLUE}uv run python -m pytest${NC}   # Run tests (when added)"
echo "- ${BLUE}uv build${NC}                   # Build package for distribution"

echo ""
print_info "Environment setup completed successfully! 🚀"