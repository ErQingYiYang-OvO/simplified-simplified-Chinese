@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 goto use_py
python -B gui.py --open
goto done
:use_py
py -3 -B gui.py --open
:done
if errorlevel 1 pause
