@echo off
title INSTALADOR NOZHGESS v3.0
color 0A

echo ========================================================
echo        INSTALADOR DE DEPENDENCIAS - NOZHGESS
echo ========================================================
echo.
echo [1/3] VERIFICANDO PYTHON...
echo.
echo NOTA IMPORTANTE:
echo Este script NO instala Python por ti.
echo Debes tener Python 3.10+ instalado desde python.org
echo Asegurate de marcar la casilla "Add Python to PATH" al instalarlo.
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR CRITICO] No se detecto Python instalado.
    echo Por favor descarga Python aqui: https://www.python.org/downloads/
    echo 1. Instala Python.
    echo 2. Reinicia tu PC.
    echo 3. Vuelve a ejecutar este archivo.
    pause
    exit /b
)

echo [OK] Python detectado correctamente.
echo.
echo --------------------------------------------------------
echo [2/3] DESCARGANDO LIBRERIAS BLINDADAS...
echo --------------------------------------------------------
echo.
echo - PANDAS / OPENPYXL: Para generar los reportes Excel con colores.
echo - SELENIUM: El motor que controla el navegador Edge.
echo - WEBDRIVER-MANAGER: Autocarga el driver de Edge (No necesitas bajarlo manual).
echo - CUSTOMTKINTER: La interfaz grafica moderna oscura.
echo - COLORAMA: Para los colores en la terminal.
echo.
echo Instalando... Por favor espera...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Hubo un problema conectando con PyPI.
    echo - Verifica tu conexion a internet.
    echo - Si estas en una red corporativa restrictiva, intenta usar otra red.
    pause
    exit /b
)

echo.
echo --------------------------------------------------------
echo [3/3] VERIFICACION FINAL
echo --------------------------------------------------------
echo.
echo Todas las librerias fueron instaladas correctamente.
echo Tu entorno esta listo para ejecutar Nozhgess.
echo.
echo ========================================================
echo           PROCESO COMPLETADO EXITOSAMENTE
echo ========================================================
echo Puedes cerrar esta ventana y ejecutar "Nozhgess.pyw" o los accesos directos.
pause
