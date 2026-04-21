@echo off
echo ============================================
echo  TTTI ERMS - Setup Script
echo ============================================

echo.
echo [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Please edit .env with your database credentials before continuing.
    pause
)

echo.
echo [4/4] Initializing database...
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python seed_data.py

echo.
echo ============================================
echo  Setup complete! Run: python run.py
echo ============================================
pause
