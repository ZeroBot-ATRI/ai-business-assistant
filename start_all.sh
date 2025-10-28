#!/bin/bash
# AI助手 - 一键启动脚本（Linux/Mac）

echo "===================================="
echo "   AI业务助手 - 一键启动"
echo "===================================="
echo ""

# 检查虚拟环境
if [ ! -f "venv/bin/activate" ]; then
    echo "[错误] 未找到虚拟环境，请先运行："
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "[1/3] 激活虚拟环境..."
source venv/bin/activate

echo ""
echo "[2/3] 启动后端API（端口8000）..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"

# 等待后端启动
sleep 3

echo ""
echo "[3/3] 启动前端界面..."

# 创建日志目录
mkdir -p logs

# 启动聊天界面（端口8501）
nohup streamlit run ui/app_enhanced.py --server.port 8501 > logs/chat.log 2>&1 &
CHAT_PID=$!
echo "聊天界面PID: $CHAT_PID"

# 启动监控看板（端口8502）
nohup streamlit run ui/dashboard.py --server.port 8502 > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "监控看板PID: $DASHBOARD_PID"

echo ""
echo "===================================="
echo "  启动完成！"
echo "===================================="
echo ""
echo "服务地址："
echo "  后端API:   http://localhost:8000"
echo "  聊天界面:  http://localhost:8501"
echo "  监控看板:  http://localhost:8502"
echo ""
echo "进程ID："
echo "  后端:     $BACKEND_PID"
echo "  聊天界面: $CHAT_PID"
echo "  监控看板: $DASHBOARD_PID"
echo ""
echo "日志文件："
echo "  后端:     logs/backend.log"
echo "  聊天界面: logs/chat.log"
echo "  监控看板: logs/dashboard.log"
echo ""
echo "停止所有服务："
echo "  kill $BACKEND_PID $CHAT_PID $DASHBOARD_PID"
echo ""
