@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   构建 AI高压沟通教练.exe （PyInstaller）
echo   生成后对方电脑无需安装 Python
echo ============================================
echo.
echo [1/2] 检查 PyInstaller...
python -c "import PyInstaller" >nul 2>nul
if %errorlevel% neq 0 (
  echo 未检测到 PyInstaller，正在安装...
  python -m pip install pyinstaller
)
echo.
echo [2/2] 开始打包（可能需要 1-3 分钟）...
python -m PyInstaller --noconfirm --clean --onefile --name "AI高压沟通教练" ^
  --add-data "index.html;." ^
  --add-data "skills;skills" ^
  server.py

echo.
if exist "dist\AI高压沟通教练.exe" (
  echo 打包成功，将 exe 复制到项目根目录...
  copy /y "dist\AI高压沟通教练.exe" "%~dp0AI高压沟通教练.exe" >nul
  echo.
  echo 清理打包临时文件...
  if exist "build" rmdir /s /q "build"
  if exist "dist" rmdir /s /q "dist"
  if exist "AI高压沟通教练.spec" del /q "AI高压沟通教练.spec"
  if exist "__pycache__" rmdir /s /q "__pycache__"
  echo.
  echo 完成：exe 已放至项目根目录 %~dp0AI高压沟通教练.exe
  echo.
  echo 使用说明：
  echo   - 对方无需安装 Python，双击 exe 即可启动
  echo   - 首次运行会解压到临时目录，需稍等 1-3 秒
  echo   - 启动后自动打开浏览器 http://localhost:8000
  echo   - 配置保存在 exe 同目录的 user_data\ 下
  echo   - 关闭黑色窗口即停止服务
) else (
  echo.
  echo 构建失败，请查看上方报错信息。
  echo 提示：若因上次残留导致失败，可先手动删除 build 文件夹后再试。
)
pause
