@echo off
REM ===============================================
REM  MingLi 一键打包脚本 (Windows)
REM  用法: 双击 build.bat 或在 cmd 中运行
REM  产物: dist\MingLi.exe
REM ===============================================
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo [1/3] 清理旧构建产物...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
for /d /r app %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /d /r tests %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

echo.
echo [2/3] 运行 PyInstaller...
python -m PyInstaller --clean --noconfirm MingLi.spec
if errorlevel 1 (
    echo.
    echo [X] 打包失败！查看上方日志。
    pause
    exit /b 1
)

echo.
echo [3/3] 拷贝运行时配置示例...
copy /Y .env.example dist\.env.example >nul

echo.
echo ===============================================
echo  [√] 打包完成: dist\MingLi.exe
echo  体积:
for %%F in (dist\MingLi.exe) do @echo       %%~zF bytes
echo.
echo  使用方法:
echo       1. 把 dist\MingLi.exe 拷到任意目录
echo       2. 在该目录创建 .env (可复制 .env.example)
echo       3. 双击 MingLi.exe 即可启动
echo ===============================================
echo.
pause
