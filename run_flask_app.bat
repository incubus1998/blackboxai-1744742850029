@echo off
REM Batch script to set environment variables and run Flask app on Windows

REM Navigate to project directory
cd /d C:\Users\Yanna\blackboxai-1744742850029

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found, continuing without activation
)

REM Set environment variables (replace placeholders with your actual values)
set FLASK_APP=app.py
set FLASK_ENV=development
set GOOGLE_CLIENT_ID=your-google-client-id
set GOOGLE_CLIENT_SECRET=your-google-client-secret
set SECRET_KEY=your-secret-key

REM Run Flask app
flask run --host=0.0.0.0 --port=8000

pause
