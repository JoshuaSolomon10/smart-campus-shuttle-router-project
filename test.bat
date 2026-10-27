@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not found. Run run.bat once first.
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
python -m pytest -q
set "RESULT=%errorlevel%"
echo.
if not "%RESULT%"=="0" echo Some tests failed. Review the output above.
pause
exit /b %RESULT%
