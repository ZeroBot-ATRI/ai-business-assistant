@echo off
chcp 65001 > nul
cls
echo ====================================
echo    AI业务助手 - 启动
echo ====================================
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

cd /d "%~dp0"

echo [1/3] 启动后端API（端口8000）...
start "后端API - 端口8000" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

ping 127.0.0.1 -n 6 > nul

echo [2/3] 启动聊天界面（端口8501）...
start "聊天界面 - 端口8501" cmd /k "python -m streamlit run ui/app_enhanced.py --server.port 8501"

ping 127.0.0.1 -n 3 > nul

echo [3/3] 启动监控看板（端口8502）...
start "监控看板 - 端口8502" cmd /k "python -m streamlit run ui/dashboard.py --server.port 8502"

echo.
echo ====================================
echo   启动完成！
echo ====================================
echo.
echo 服务地址：
echo   - 后端API文档:  http://localhost:8000/docs
echo   - 聊天界面:      http://localhost:8501
echo   - 监控看板:      http://localhost:8502
echo.
echo 提示：
echo   - 已打开3个命令窗口，关闭窗口即停止对应服务
echo   - 在服务窗口按 Ctrl+C 可停止服务
echo.
pause
