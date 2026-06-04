@echo off
chcp 65001 >nul
title vision-learning 环境安装

echo ========================================
echo   vision-learning 依赖安装脚本
echo   安装：opencv-python / pyzbar / qrcode
echo ========================================
echo.

REM 备份当前代理设置
echo [1/3] 临时关闭系统代理...
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable') do set OLD_PROXY=%%a
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul
) else (
    set OLD_PROXY=0
)

REM 清除环境变量中的代理
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=

echo [2/3] 安装 Python 包...
pip install opencv-python pyzbar qrcode[pil] -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if %errorlevel% neq 0 (
    echo.
    echo ⚠ 安装失败，尝试直接连接 PyPI...
    pip install opencv-python pyzbar qrcode[pil]
)

echo.
echo [3/3] 恢复代理设置...
if "%OLD_PROXY%"=="1" (
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f >nul
)

echo.
echo ========================================
echo   安装完成！
echo.
echo   验证安装：python -c "import cv2; print('OpenCV', cv2.__version__)"
echo ========================================

pause
