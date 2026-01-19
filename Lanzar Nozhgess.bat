@echo off
REM Launcher script para Nozhgess
REM Ejecuta la aplicación GUI

cd /d "%~dp0"

echo ========================================
echo    NOZHGESS - Iniciando aplicación
echo ========================================
echo.

REM Activar venv si existe
if exist ".venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM Ejecutar aplicación
echo Iniciando GUI...
pythonw Nozhgess.pyw

REM Si pythonw no funciona, usar python normal
if errorlevel 1 (
    echo.
    echo pythonw no disponible, usando python...
    python Nozhgess.pyw
    pause
)
