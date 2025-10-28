@echo off
chcp 65001 > nul
echo ====================================
echo    AI业务助手 - 启动脚本
echo ====================================
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python
    pause
    exit /b 1
)

echo [1/3] 启动后端API（端口8000）...
start "后端API" /B cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo 等待后端启动...
ping 127.0.0.1 -n 6 > nul

echo.
echo [2/3] 启动聊天界面（端口8501）...
start "聊天界面" /B cmd /c "python -m streamlit run ui/app_enhanced.py --server.port 8501"

echo 等待界面启动...
ping 127.0.0.1 -n 3 > nul

echo.
echo [3/3] 启动监控看板（端口8502）...
start "监控看板" /B cmd /c "python -m streamlit run ui/dashboard.py --server.port 8502"

echo.
echo ====================================
echo   启动完成！
echo ====================================
echo.
echo 服务地址：
echo   - 后端API:   http://localhost:8000
echo   - 后端文档:  http://localhost:8000/docs
echo   - 聊天界面:  http://localhost:8501
echo   - 监控看板:  http://localhost:8502
echo.
echo 提示：
echo   - 所有服务在后台运行
echo   - 使用 taskkill /F /IM python.exe 停止所有服务
echo   - 或在任务管理器中结束 python.exe 进程
echo.
pause
