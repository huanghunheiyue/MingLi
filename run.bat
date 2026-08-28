@echo off
chcp 65001 >nul
REM ===========================================
REM 明礼 MingLi · Windows 一键启动脚本
REM ===========================================
cd /d "%~dp0"

echo ========================================
echo   明礼 MingLi · 明代历史文化科普智能体
echo ========================================

if not exist ".env" (
  echo [!] .env 不存在，从 .env.example 复制
  copy .env.example .env
  echo [!] 请编辑 .env 填入真实 API Key 后再次运行
  pause
  exit /b 1
)

echo [*] 启动服务 http://localhost:8000
python -X utf8 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause