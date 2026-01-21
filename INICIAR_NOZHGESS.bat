@echo off
TITLE Nozhgess Launcher
CLS
ECHO ====================================================
ECHO             INICIANDO NOZHGESS...
ECHO ====================================================
ECHO.
ECHO Verificando librerias necesarias...

python -c "import customtkinter" 2>NUL
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    COLOR 0E
    ECHO ====================================================
    ECHO [AVISO] FALTAN LIBRERIAS
    ECHO ====================================================
    ECHO Instalando customtkinter y dependencias...
    ECHO Por favor espere, esto solo pasara una vez.
    ECHO.
    pip install customtkinter packaging pillow mousetools
    ECHO.
    ECHO Instalacion finalizada.
    COLOR 07
    ECHO.
)

ECHO Iniciando Nozhgess...
python App/Nozhgess.pyw

