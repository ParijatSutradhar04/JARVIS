@echo off
echo 🤖 JARVIS Voice AI Agent - Windows Setup
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys
)

echo.
echo 🎉 Setup complete!
echo.
echo 📝 Next steps:
echo 1. Edit .env file with your OpenAI API key
echo 2. Run: python main.py
echo.
echo 🧪 To test the setup: python test.py
echo.

pause
