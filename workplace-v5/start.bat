@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set "AHC_AUTO_OPEN=1"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
title AI Workplace Communication Coach
python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >nul 2>nul
if not errorlevel 1 goto run_python
py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 goto run_py
echo Python 3 was not found. Install Python 3 and select Add Python to PATH.
pause
exit /b 1

:run_python
python -u server.py 8000
goto finished

:run_py
py -3 -u server.py 8000

:finished
if errorlevel 1 (
  echo.
  echo Startup failed. Please check the error above.
  pause
)
endlocal
