@echo off
:: ==============================================================================
::                    NOZHGESS - INSTALADOR SIMPLE
:: ==============================================================================
:: Este script crea un acceso directo en el escritorio.
:: Ejecutar una sola vez.
:: ==============================================================================

echo.
echo ========================================
echo   INSTALADOR DE NOZHGESS v3.0
echo ========================================
echo.

:: Obtener rutas
set "SCRIPT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGET=%SCRIPT_DIR%App\Nozhgess.pyw"

echo Creando acceso directo en el escritorio...

:: Crear shortcut usando PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$s = $ws.CreateShortcut('%DESKTOP%\Nozhgess.lnk'); " ^
    "$s.TargetPath = 'pythonw.exe'; " ^
    "$s.Arguments = '\"%TARGET%\"'; " ^
    "$s.WorkingDirectory = '%SCRIPT_DIR%'; " ^
    "$s.Description = 'Nozhgess - Automatizacion de Datos Medicos'; " ^
    "$s.Save()"

if exist "%DESKTOP%\Nozhgess.lnk" (
    echo.
    echo ========================================
    echo   INSTALACION COMPLETADA!
    echo ========================================
    echo.
    echo Acceso directo creado en: %DESKTOP%\Nozhgess.lnk
    echo.
    echo Ahora puedes abrir Nozhgess desde el escritorio.
    echo.
) else (
    echo.
    echo ERROR: No se pudo crear el acceso directo.
    echo.
)

pause
