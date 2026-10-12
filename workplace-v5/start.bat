@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动 AI职场沟通训练师 v5...
where python >nul 2>nul
if %errorlevel% equ 0 (
  python -u server.py 8000
) else (
  py -3 -u server.py 8000
)
pause
