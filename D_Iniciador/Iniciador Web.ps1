# Iniciador Web para NOZHGESS v1.0
# Abre Edge en modo debug para conexión con Selenium

$EdgePath = "msedge.exe"
$SiggesUrl = "https://www.sigges.cl"
$DebugPort = 9222
$ProfileDir = "C:\Selenium\EdgeProfile"

Write-Host "🌐 Iniciando Edge en modo debug..." -ForegroundColor Cyan
Write-Host "   URL: $SiggesUrl" -ForegroundColor Gray
Write-Host "   Puerto debug: $DebugPort" -ForegroundColor Gray

Start-Process $EdgePath "$SiggesUrl --remote-debugging-port=$DebugPort --user-data-dir=$ProfileDir"

Write-Host "✅ Edge iniciado correctamente" -ForegroundColor Green
Write-Host "   Ahora puede ejecutar el script de revisión" -ForegroundColor Yellow
