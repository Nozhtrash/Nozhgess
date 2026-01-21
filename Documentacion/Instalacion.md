# Guía de Instalación - Nozhgess v3.0

## 1. Requisitos Previos

Antes de instalar Nozhgess, asegúrate de tener:
- **Windows 10 o superior**.
- **Python 3.10** instalado (Asegúrate de marcar "Add Python to PATH" durante la instalación).
- **Microsoft Edge** actualizado.

## 2. Instalación Rápida

1. Descarga o clona este repositorio en una carpeta de tu preferencia.
2. Haz doble clic en el archivo `INSTALAR.bat` ubicado en la carpeta raíz.
3. Este script creará automáticamente un acceso directo llamado **Nozhgess** en tu escritorio.

## 3. Primer Inicio

- Haz doble clic en el acceso directo del escritorio o en `INICIAR_NOZHGESS.bat`.
- La primera vez, la aplicación verificará e instalará las librerías necesarias (esto puede tardar unos minutos).
- Una vez finalizado, se abrirá la interfaz gráfica de Nozhgess.

## 4. Configuración del Navegador

Para que la automatización funcione, debes iniciar Edge en modo de depuración:
- Ve a la carpeta `Iniciador/`.
- Ejecuta `Iniciador Web.ps1` (Clic derecho -> Ejecutar con PowerShell).
- Esto abrirá una ventana de Edge especial que Nozhgess puede controlar.

## 5. Solución de Problemas

- **Python no encontrado**: Reinstala Python y asegúrate de marcar la opción "Add to PATH".
- **Faltan librerías**: Ejecuta `INICIAR_NOZHGESS.bat` para forzar la reinstalación de dependencias.
- **Acceso denegado**: Ejecuta los scripts `.bat` como administrador si es necesario.
