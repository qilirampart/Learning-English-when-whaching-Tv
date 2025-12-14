@echo off
chcp 65001 >nul
echo ================================
echo     pip 安装助手
echo ================================
echo.
echo 使用说明：
echo 1. 请手动在 Clash 中关闭"系统代理"
echo 2. 然后按任意键继续安装
echo 3. 安装完成后记得重新开启"系统代理"
echo.
pause
echo.
echo 正在使用清华源安装...
echo.

REM 使用清华源安装
pip install %* -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo ================================
echo     安装完成！
echo ================================
echo.
echo 请记得在 Clash 中重新开启"系统代理"
echo.
pause
