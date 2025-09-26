@echo off
REM Web Content Analyzer - Windows Setup Script
REM This script initializes a clean environment with all dependencies

echo.
echo 🚀 Web Content Analyzer - Environment Setup
echo ==============================================

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo ❌ pyproject.toml not found. Please run this script from the web-content-analyzer directory.
    pause
    exit /b 1
)

echo ℹ️  Setting up Web Content Analyzer environment...

REM Step 1: Check if uv is installed
echo.
echo Step 1: Checking uv installation...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  uv not found. Please install uv manually.
    echo    Visit: https://docs.astral.sh/uv/getting-started/installation/
    echo    Run: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('uv --version') do set UV_VERSION=%%i
    echo ✅ uv is installed: !UV_VERSION!
)

REM Step 2: Check Python version
echo.
echo Step 2: Checking Python version...
echo ℹ️  Python 3.12+ will be managed automatically by uv

REM Step 3: Install project dependencies
echo.
echo Step 3: Installing project dependencies...
echo ℹ️  This may take a few minutes on first run...

uv sync
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Project dependencies installed successfully

REM Step 4: Install Playwright browsers
echo.
echo Step 4: Installing Playwright browsers...
echo ℹ️  Installing Chromium browser for web scraping...

uv run playwright install chromium
if %errorlevel% neq 0 (
    echo ❌ Failed to install Playwright browsers
    pause
    exit /b 1
)

echo ✅ Playwright browsers installed successfully

REM Step 5: Set up environment configuration
echo.
echo Step 5: Setting up environment configuration...

if not exist ".env" (
    echo ℹ️  Creating .env file from template...
    copy ".env.example" ".env" >nul
    echo ⚠️  IMPORTANT: Edit .env file and add your ANTHROPIC_API_KEY
    echo    Get your API key from: https://console.anthropic.com/settings/keys
) else (
    echo ✅ .env file already exists
)

REM Step 6: Verify installation
echo.
echo Step 6: Verifying installation...

uv run python -c "import sys; sys.path.insert(0, 'src'); from web_content_analyzer.simple_analyzer import SimpleWebContentAnalyzer; from web_content_analyzer.config import Config; print('✅ All modules imported successfully')" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Module import verification failed
    pause
    exit /b 1
)

echo ✅ Module imports working correctly

uv run python analyze.py --help >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ CLI script verification failed
    pause
    exit /b 1
)

echo ✅ CLI script working correctly

REM Step 7: Display usage information
echo.
echo 🎉 Setup Complete!
echo ==================
echo ✅ Web Content Analyzer is ready to use!

echo.
echo 📋 Next Steps:
echo 1. Edit .env file and add your ANTHROPIC_API_KEY
echo    notepad .env
echo.
echo 2. Test with a single URL:
echo    set ANTHROPIC_API_KEY=your_key_here
echo    uv run python analyze.py https://example.com
echo.
echo 3. Test batch processing:
echo    uv run python analyze.py batch examples\urls.txt
echo.
echo 4. Use the uv package directly:
echo    uvx --from . web-analyzer analyze https://example.com

echo.
echo 📖 Documentation:
echo - README.md for detailed usage instructions
echo - examples\urls.txt for sample input
echo - GitHub: https://github.com/eovidiu/web-content-analyzer

echo.
echo 🔧 Development commands:
echo - uv sync                    # Update dependencies
echo - uv run python -m pytest   # Run tests (when added)
echo - uv build                   # Build package for distribution

echo.
echo ℹ️  Environment setup completed successfully! 🚀
echo.
pause