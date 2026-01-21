@echo off
:: Desinstala Nozhgess (elimina acceso directo)
echo Eliminando acceso directo...
del "%USERPROFILE%\Desktop\Nozhgess.lnk" 2>nul
echo Desinstalacion completada.
pause
