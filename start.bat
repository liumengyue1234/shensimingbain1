@echo off
chcp 65001 >nul
echo ============================================
echo   审思明辨——智判法案双擎系统
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装 Python 依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo     依赖安装完成

:: 检查 .env
if not exist .env (
    echo [2/3] 未找到 .env 文件，正在从模板创建...
    copy .env.example .env >nul
    echo     已创建 .env，请编辑填入你的 API 密钥
    echo.
    echo     需要配置的关键参数：
    echo     - YUANQI_APP_ID / YUANQI_APP_KEY  （腾讯元器智能体，可选）
    echo.
) else (
    echo [2/3] 已找到 .env 配置文件
)

:: 启动服务
echo [3/3] 启动服务...
echo.
echo ============================================
echo   访问地址：http://localhost:8000
echo   按 Ctrl+C 停止服务
echo ============================================
echo.
python app.py
pause
