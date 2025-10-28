@echo off
chcp 65001 > nul
REM AI助手 - 简化启动脚本（直接使用Python，不需要虚拟环境）

echo ====================================
echo    AI业务助手 - 简化启动
echo ====================================
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1/3] 启动后端API（端口8000）...
start "AI助手-后端API" cmd /k python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

echo 等待后端启动（5秒）...
timeout /t 5 /nobreak > nul

echo.
echo [2/3] 启动聊天界面（端口8501）...
start "AI助手-聊天界面" cmd /k python -m streamlit run ui/app_enhanced.py --server.port 8501

echo 等待界面启动（2秒）...
timeout /t 2 /nobreak > nul

echo.
echo [3/3] 启动监控看板（端口8502）...
start "AI助手-监控看板" cmd /k python -m streamlit run ui/dashboard.py --server.port 8502

echo.
echo ====================================
echo   启动完成！
echo ====================================
echo.
echo 服务地址：
echo   后端API:   http://localhost:8000
echo   后端文档:  http://localhost:8000/docs
echo   聊天界面:  http://localhost:8501
echo   监控看板:  http://localhost:8502
echo.
echo 提示：
echo - 关闭窗口将停止对应服务
echo - 按 Ctrl+C 可停止服务
echo.
echo 按任意键关闭此启动窗口...
pause > nul
