@echo off
echo ============================================
echo  Yatra AI — Setup Script (Windows)
echo ============================================
echo.

echo [1/4] Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (echo ERROR: Python not found. Install Python 3.11+ && exit /b 1)

echo [2/4] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt

echo [4/4] Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo.
    echo IMPORTANT: Open backend\.env and add your GEMMA_API_KEY
    echo Get your key from: https://aistudio.google.com/apikey
) else (
    echo .env already exists — skipping.
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo Next steps:
echo  1. Edit backend\.env and set GEMMA_API_KEY=your_key_here
echo  2. Run: cd backend ^& .venv\Scripts\activate ^& python main.py
echo  3. Open frontend\index.html in your browser
echo.
pause
