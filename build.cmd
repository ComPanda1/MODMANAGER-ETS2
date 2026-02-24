@echo off
setlocal
title Building ETS2 - Mod Manager
echo.
echo [1/4] Instalando dependencias necesarias...
pip install -r requirements.txt --quiet

echo [2/4] Limpiando carpetas de compilaciones previas...
if exist dist del /q dist\*.*
if exist build rd /s /q build

echo [3/4] Compilando ejecutable (esto puede tardar un momento)...
:: --onefile: Crea un unico archivo .exe para que no necesite nada mas.
:: --uac-admin: Solicita permisos de administrador al abrirse.
:: --icon: Aplica el icono personalizado.
:: --clean: Limpia la cache de PyInstaller antes de compilar.
pyinstaller --noconfirm --onefile --console --icon="Manager.ico" --name "Manager" --clean Manager.py

echo.
echo [4/4] Finalizando...
if exist "Manager.spec" del "Manager.spec"

echo.
echo Finalizado con exito. El archivo esta en la carpeta 'dist'.
pause