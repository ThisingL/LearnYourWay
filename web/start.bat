@echo off
echo ========================================
echo   LearnYourWay Web 演示界面
echo ========================================
echo.
echo 启动简单 HTTP 服务器...
echo 访问地址: http://localhost:3000
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python -m http.server 3000
