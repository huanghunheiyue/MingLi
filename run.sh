#!/usr/bin/env bash
# ============================================
# 明礼 MingLi · 一键启动脚本
# ============================================
set -e

cd "$(dirname "$0")"

echo "========================================"
echo "  明礼 MingLi · 明代历史文化科普智能体"
echo "========================================"

# 检查 .env
if [ ! -f ".env" ]; then
  echo "[!] .env 不存在，从 .env.example 复制"
  cp .env.example .env
  echo "[!] 请编辑 .env 填入真实 API Key 后再次运行"
  exit 1
fi

# 检查依赖
if [ ! -d ".venv" ]; then
  echo "[*] 创建虚拟环境"
  python3 -m venv .venv
fi

source .venv/bin/activate 2>/dev/null || .venv\Scripts\activate.bat

echo "[*] 安装依赖"
pip install -r requirements.txt -q

echo ""
echo "[*] 启动服务"
echo "    http://localhost:8000"
echo ""

# 选择是否暴露公网
if [ -n "$NGROK_TOKEN" ]; then
  echo "[*] 检测到 NGROK_TOKEN，启动 ngrok 暴露公网"
  uvicorn app.main:app --host 0.0.0.0 --port 8000 &
  UVICORN_PID=$!
  sleep 3
  ngrok http 8000 --authtoken "$NGROK_TOKEN" &
  NGROK_PID=$!
  trap "kill $UVICORN_PID $NGROK_PID 2>/dev/null" EXIT
  wait
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi