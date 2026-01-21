$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcut = $ws.CreateShortcut("$desktop\Nozhgess.lnk")
$shortcut.TargetPath = "pythonw.exe"
$shortcut.Arguments = "`"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original\Nozhgess.pyw`""
$shortcut.WorkingDirectory = "c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original"
$shortcut.Description = "Nozhgess - Automatizacion de Datos Medicos"
$shortcut.Save()
Write-Host "Acceso directo 'Nozhgess' creado en el escritorio!"
