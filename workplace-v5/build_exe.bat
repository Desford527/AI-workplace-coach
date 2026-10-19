@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 构建 AI职场沟通训练师 v5，需在 Windows 上安装 Python 和 PyInstaller。
python -c "import PyInstaller" >nul 2>nul
if %errorlevel% neq 0 (
  echo 请先执行 python -m pip install pyinstaller，再运行此脚本。
  pause
  exit /b 1
)
python -m PyInstaller --noconfirm --clean --onefile --name "AI职场沟通训练师" ^
 --add-data "index.html;." ^
 --add-data "web;web" ^
 --add-data "workplace-data.json;." ^
 --add-data "default-api.json;." ^
 --add-data "skills;skills" ^
 --hidden-import workplace --hidden-import workspace_tools --hidden-import meetings server.py
if %errorlevel% neq 0 (
  echo 构建失败，未生成可交付 exe。
  pause
  exit /b 1
)
echo 输出：dist\AI职场沟通训练师.exe。未打包 user_data；包含用户授权的默认 API 配置。
echo 新 exe 的首次真实模型、配置持久化及桌面功能仍需在 Windows 验证。
pause
