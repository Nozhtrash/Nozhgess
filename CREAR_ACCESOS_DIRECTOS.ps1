$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetFile = Join-Path $ScriptDir "Nozhgess.pyw"
$IconFile = Join-Path $ScriptDir "App\assets\icon.ico" # Asumiendo ruta, si no existe windows usa default
$DesktopPath = [Environment]::GetFolderPath("Desktop")

# Función para crear acceso directo
function Create-Shortcut {
    param (
        [string]$ShortcutPath,
        [string]$Target,
        [string]$WorkDir,
        [string]$Description
    )
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $Target
    $Shortcut.WorkingDirectory = $WorkDir
    $Shortcut.Description = $Description
    
    # Intentar poner icono si existe
    if (Test-Path "$WorkDir\App\assets\icon.ico") {
        $Shortcut.IconLocation = "$WorkDir\App\assets\icon.ico"
    }
    elseif (Test-Path "$WorkDir\App\src\gui\assets\icon.ico") {
        # Fallback location check
        $Shortcut.IconLocation = "$WorkDir\App\src\gui\assets\icon.ico"
    }
    
    $Shortcut.Save()
    Write-Host "✅ Acceso directo creado: $ShortcutPath" -ForegroundColor Green
}

Write-Host "======================================"
Write-Host "   CREADOR DE ACCESOS DIRECTOS"
Write-Host "======================================"
Write-Host ""

if (-not (Test-Path $TargetFile)) {
    Write-Error "No se encuentra Nozhgess.pyw en: $TargetFile"
    exit
}

# 1. Crear en Escritorio
$DesktopLink = Join-Path $DesktopPath "Nozhgess.lnk"
Create-Shortcut -ShortcutPath $DesktopLink -Target $TargetFile -WorkDir $ScriptDir -Description "Lanzador Nozhgess"

# 2. Crear en la Carpeta Raíz (Main Branch)
$RootLink = Join-Path $ScriptDir "ACCESO_NOZHGESS.lnk"
Create-Shortcut -ShortcutPath $RootLink -Target $TargetFile -WorkDir $ScriptDir -Description "Lanzador Nozhgess (Root)"

Write-Host ""
Write-Host "✨ Proceso finalizado."
Start-Sleep -Seconds 3
