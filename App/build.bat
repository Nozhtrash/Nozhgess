@echo off
:: ==============================================================================
::                    BUILD SCRIPT - NOZHGESS v3.0 LEGENDARY
:: ==============================================================================
:: Script para crear el ejecutable y el instalador.
::
:: Requisitos:
::   - Python 3.10+
::   - PyInstaller: pip install pyinstaller
::   - Inno Setup (opcional, para el instalador)
::
:: Uso:
::   build.bat          - Solo crea el EXE
::   build.bat full     - Crea EXE + Instalador
:: ==============================================================================

cd /d "%~dp0"

echo.
echo ==========================================
echo   NOZHGESS BUILD SCRIPT v3.0 LEGENDARY
echo ==========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado en PATH
    exit /b 1
)

:: Verificar PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

:: Limpiar builds anteriores
echo [1/4] Limpiando builds anteriores...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

:: Crear EXE
echo [2/4] Creando ejecutable...
pyinstaller nozhgess.spec --noconfirm
if errorlevel 1 (
    echo ERROR: Fallo al crear el ejecutable
    exit /b 1
)

echo.
echo [OK] Ejecutable creado en: dist\Nozhgess\Nozhgess.exe
echo.

:: Crear instalador si se pide
if "%1"=="full" (
    echo [3/4] Creando instalador...
    
    :: Verificar Inno Setup
    if exist "%PROGRAMFILES(X86)%\Inno Setup 6\ISCC.exe" (
        "%PROGRAMFILES(X86)%\Inno Setup 6\ISCC.exe" installer.iss
        echo.
        echo [OK] Instalador creado en: Output\NozhgessSetup.exe
    ) else (
        echo ADVERTENCIA: Inno Setup no encontrado
        echo Instala Inno Setup 6 para crear el instalador
    )
)

echo.
echo [4/4] Build completado!
echo.
echo Archivos generados:
dir /b dist\Nozhgess\*.exe 2>nul
if exist "Output\NozhgessSetup.exe" dir /b Output\*.exe

pause
