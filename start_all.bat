@echo off
chcp 65001 > nul
REM AI助手 - 一键启动脚本（Windows）
echo ====================================
echo    AI业务助手 - 一键启动
echo ====================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境，请先运行：
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo [1/3] 检查环境...
set VENV_PYTHON=%CD%\venv\Scripts\python.exe
set VENV_DIR=%CD%\venv\Scripts

if not exist "%VENV_PYTHON%" (
    echo [错误] 找不到Python: %VENV_PYTHON%
    pause
    exit /b 1
)

echo 虚拟环境路径: %VENV_DIR%

echo.
echo [2/3] 启动后端API（端口8000）...
start "AI助手-后端API" cmd /k "cd /d %CD% && %VENV_DIR%\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM 等待后端启动
echo 等待后端启动...
timeout /t 5 /nobreak > nul

echo.
echo [3/3] 启动前端界面...

REM 启动聊天界面（端口8501）
start "AI助手-聊天界面" cmd /k "cd /d %CD% && %VENV_DIR%\activate.bat && streamlit run ui\app_enhanced.py --server.port 8501"

REM 等待2秒
timeout /t 2 /nobreak > nul

REM 启动监控看板（端口8502）
start "AI助手-监控看板" cmd /k "cd /d %CD% && %VENV_DIR%\activate.bat && streamlit run ui\dashboard.py --server.port 8502"

echo.
echo ====================================
echo   启动完成！
echo ====================================
echo.
echo 服务地址：
echo   后端API:   http://localhost:8000
echo   聊天界面:  http://localhost:8501
echo   监控看板:  http://localhost:8502
echo.
echo 按任意键关闭此窗口...
pause > nul
