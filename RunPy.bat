@echo off
:: 将控制台代码页更改为 UTF-8
chcp 65001 > nul
:: 运行程序
if "%~1"=="" (
    echo %1 是空的
	start "QRJS" %USERPROFILE%\miniconda3\envs\qrjs\python.exe %CD%\server.py
) else (
    echo %1 不是空的
	cd /d %1
	start "QRJS" %USERPROFILE%\miniconda3\envs\qrjs\python.exe %1\server.py
)
:: 等待用户按任意键继续
:: pause
exit