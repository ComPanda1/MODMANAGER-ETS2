@echo off
setlocal
chcp 65001 >nul
title ETS2 Mod Manager

:: Verificar si colorama está instalado
python -c "import colorama" 2>nul
if %errorlevel% neq 0 (
    echo Instalando componentes visuales...
    pip install colorama --quiet
)

:: Ejecutar el script
python Manager.py
pause