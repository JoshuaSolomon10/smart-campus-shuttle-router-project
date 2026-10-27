@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo   Smart Campus Shuttle Router
echo ==========================================
where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python 3 was not found. Install Python 3.10 or newer from python.org.
    echo Make sure "Add Python to PATH" is selected.
    pause
    exit /b 1
  )
  set "PYTHON=python"
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  %PYTHON% -m venv .venv
  if errorlevel 1 (echo ERROR: Could not create virtual environment.& pause & exit /b 1)
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 (echo ERROR: Could not activate virtual environment.& pause & exit /b 1)
python -m pip --version >nul 2>nul
if errorlevel 1 (echo ERROR: pip is unavailable.& pause & exit /b 1)
if not exist ".venv\requirements-installed.txt" (
  echo Installing project dependencies. Internet is needed for this first installation.
  python -m pip install --upgrade pip
  if errorlevel 1 (echo ERROR: pip upgrade failed.& pause & exit /b 1)
  python -m pip install -r requirements.txt
  if errorlevel 1 (echo ERROR: dependency installation failed.& pause & exit /b 1)
  echo installed>".venv\requirements-installed.txt"
)
echo Starting Streamlit...
python -m streamlit run app.py
if errorlevel 1 (echo Application exited with an error.)
pause
