@echo off
echo Starting Yatra AI Backend...
cd /d "%~dp0backend"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Run setup.bat first.
    pause & exit /b 1
)
echo Backend running at: http://localhost:8000
echo API Docs at:        http://localhost:8000/docs
echo.
python main.py
pause
