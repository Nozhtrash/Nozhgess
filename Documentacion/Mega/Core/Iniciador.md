# Iniciador del Script (`Iniciador Script.py`)

## 📌 Propósito y Definición
Este archivo es el **Punto de Entrada (Entry Point)** de toda la automatización. Su única responsabilidad es preparar el entorno de Python (sys.path) y lanzar el proceso de revisión principal.

> [!NOTE]
> No contiene lógica de negocio, solo "fontanería" para que los imports funcionen.

## ⚙️ Mecánica de Funcionamiento

### 1. Inyección de Paths
El problema histórico de Python es no encontrar los módulos cuando se ejecutan scripts desde subcarpetas.
`Iniciador Script.py` resuelve esto inyectando dinámicamente dos rutas al `sys.path`:
1.  **Raíz del Proyecto**: Para imports absolutos.
2.  **Carpeta `App`**: Para imports que comienzan con `src`.

```python
# Código crítico para que funcione 'import src'
ruta_app = os.path.join(ruta_proyecto, "App")
if ruta_app not in sys.path:
    sys.path.insert(0, ruta_app)
```

### 2. Lanzamiento del Motor
Importa y ejecuta `ejecutar_revision()` desde `Utilidades.Mezclador.Conexiones`.
Todo el script está envuelto en un bloque `try-except` gigante para capturar **Cualquier** error no manejado y mostrar el `traceback` completo antes de cerrarse, evitando que la ventana negra se cierre instantáneamente sin dejar ver el error.

## 🛠️ Dependencias Externas
*   **`Iniciador Web.ps1`**: Este script de PowerShell es **OBLIGATORIO** para iniciar el navegador Edge.
    *   **Puerto 9222**: El script asume *siempre* que Edge está corriendo en el puerto 9222 (`--remote-debugging-port=9222`).
    *   **Perfil de Usuario**: Usa `C:\Selenium\EdgeProfile` para mantener la sesión de SIGGES iniciada (cookies).

## ⚠️ Debilidades y Puntos de Falla (Honestidad Brutal)
1.  **Dependencia del PowerShell**: Si el usuario abre Edge manualmente (doble click), el script **NO FUNCIONARÁ**. Debe usarse `Iniciador Web.ps1` porque Selenium necesita el puerto de debug abierto.
2.  **Rutas Estáticas**: Si mueves la carpeta del proyecto a una ruta con caracteres muy extraños o permisos restringidos, `os.path.dirname` podría fallar en entornos Windows antiguos (aunque raro en Win10/11).
3.  **Import Recursivo**: Si `Conexiones.py` falla al importarse (ej: error de sintaxis en un submódulo), el `try-except` en `Iniciador Script.py` capturará el error, pero el script morirá inmediatamente.

## 🐛 Historial de Bugs Relevantes
*   **"ModuleNotFoundError: No module named 'src'"**: Fue el bug más común en versiones v0.5. Se solucionó agregando la inyección de `App` al path (Líneas 16-19).
