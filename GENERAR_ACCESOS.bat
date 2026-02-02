@echo off
echo Creando accesos directos...
powershell -ExecutionPolicy Bypass -File "CREAR_ACCESOS_DIRECTOS.ps1"
if %errorlevel% neq 0 (
    echo Error creando accesos directos.
    pause
)
del "CREAR_ACCESOS_DIRECTOS.ps1"
