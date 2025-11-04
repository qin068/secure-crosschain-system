#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}   可信跨链系统 - 一键启动（稳定版）${NC}"
echo -e "${GREEN}=================================================${NC}"

# ---------- 1. 激活虚拟环境 ----------
if [ ! -f "$ROOT_DIR/.venv/bin/activate" ]; then
    echo -e "${RED}未找到 .venv，请运行：python3 -m venv .venv${NC}"
    exit 1
fi
echo -e "${YELLOW}[1/5] 激活 Python 虚拟环境...${NC}"
source "$ROOT_DIR/.venv/bin/activate"

# ---------- 2. 检查 Node ----------
# if ! command -v node &> /dev/null; then
#     echo -e "${RED}未找到 node，请安装 Node.js${NC}"
#     exit 1
# fi
# echo -e "${GREEN}Node.js: $(node -v), npm: $(npm -v)${NC}"
echo -e "${GREEN}Node.js 已检测（系统全局安装）${NC}"

# ---------- 3. 启动 TPM ----------
echo -e "${YELLOW}[2/5] 启动 TPM 服务...${NC}"
cd "$ROOT_DIR/tpm_driver"
if [ ! -f "tpm2-http-server" ]; then
    echo "编译 TPM 服务..."
    make clean && make
fi
pkill -f tpm2-http-server 2>/dev/null || true
./tpm2-http-server > tpm.log 2>&1 &
TPM_PID=$!
sleep 3
cd "$ROOT_DIR"

# ---------- 4. 启动 FastAPI ----------
echo -e "${YELLOW}[3/5] 启动后端...${NC}"
cd "$ROOT_DIR/backend"
pip install -r requirements.txt > /dev/null 2>&1
pkill -f "uvicorn main:app" 2>/dev/null || true
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
sleep 3
cd "$ROOT_DIR"

# ---------- 5. 启动 Vue ----------
echo -e "${YELLOW}[4/5] 启动前端...${NC}"
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install > /dev/null 2>&1
fi
pkill -f "vite" 2>/dev/null || true
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 3
cd "$ROOT_DIR"

echo -e "${GREEN}所有服务启动成功！${NC}"
echo "浏览器打开：http://localhost:5173"
echo ""
echo "停止命令："
echo "  pkill -f tpm2-http-server"
echo "  pkill -f uvicorn"
echo "  pkill -f vite"
echo -e "${NC}"