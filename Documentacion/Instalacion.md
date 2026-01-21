# ⚙️ Guía de Instalación y Configuración Detallada

Esta guía proporciona los pasos necesarios para desplegar Nozhgess v3.0 en tu entorno local de forma profesional y segura.

---

## 1. Requisitos de Sistema

*   **Sistema Operativo**: Windows 10/11 (arquitectura de 64 bits recomendada).
*   **Procesador**: Mínimo 2 núcleos (4 o más recomendados para el modo normal).
*   **Memoria RAM**: 4 GB mínimo (8 GB recomendados).
*   **Software Adicional**:
    *   **Python 3.10 o superior**: Es vital marcar la casilla **"Add Python to PATH"** durante la instalación.
    *   **Microsoft Edge**: Versión actualizada.

---

## 2. Instalación Paso a Paso

### Método A: Para el Usuario Final (Manual)
1.  **Descarga**: Clona o descarga el repositorio en una carpeta estable (evita el Escritorio o descargas para mayor velocidad).
2.  **Instalación**: Haz doble clic en el archivo [`INSTALAR.bat`](file:///INSTALAR.bat).
    *   *¿Qué hace este archivo?*: Crea un acceso directo profesional en tu escritorio con el ícono oficial de Nozhgess.
3.  **Verificación**: Abre el acceso directo. La aplicación detectará automáticamente si faltan librerías y las instalará por ti.

### Método B: Para Desarrolladores (Git/IDE)
1.  Clona el repositorio: `git clone https://github.com/Nozhtrash/Nozhgess.git`.
2.  Crea un entorno virtual (opcional pero recomendado): `python -m venv .venv`.
3.  Activa el entorno: `.venv\Scripts\activate`.
4.  Instala dependencias: `pip install -r App/requirements.txt`.

---

## 3. Configuración del Navegador (Crítico)

Nozhgess interactúa con una ventana de Edge específica. Sigue estos pasos:
1.  Cierra todas las ventanas de Microsoft Edge.
2.  Ve a la carpeta **`Iniciador/`**.
3.  Ejecuta **`Iniciador Web.ps1`** (Clic derecho -> Ejecutar con PowerShell).
4.  Se abrirá una ventana de Edge con un borde especial. **No la cierres**. Úsala para entrar al portal SIGGES.

---

## 4. Resolución de Problemas (Troubleshooting)

| Problema | Solución |
| :--- | :--- |
| **"Python is not recognized"** | Reinstala Python y asegúrate de marcar "Add to PATH". |
| **Error de Selenium/Driver** | Asegúrate de que el navegador Edge en modo debug esté abierto. Si persiste, borra la carpeta `App/__pycache__`. |
| **La app se queda pegada** | Activa el **"Modo Potato"** en la configuración de la derecha para reducir el uso de CPU. |
| **Falta de permisos** | Ejecuta la aplicación o los scripts `.bat` como Administrador. |

---

## 5. Mantenimiento
Para mantener Nozhgess funcionando al 100%:
*   Limpia periódicamente la carpeta **`Logs/`**.
*   Verifica que los archivos Excel en **`Lista de Misiones/`** tengan el formato correcto según el [Manual del Usuario](file:///Documentacion/Manual_Usuario.md).

---
© 2026 Nozhgess Team.
