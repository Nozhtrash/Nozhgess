# 🔧 Guía de Solución de Problemas (Troubleshooting)

> **Ayuda Rápida para Operadores y Desarrolladores**

Esta guía cubre los problemas más comunes encontrados durante la operación de **Nozhgess** y sus soluciones definitivas. Úsala antes de abrir un reporte de error.

---

## 🚨 Problemas Críticos Comunes

### 1. "Timeout esperando elemento" / Spinner Pegado
**Síntoma:** El script se queda esperando indefinidamente con el mensaje `⏳ Esperando desaparición de spinner...` o falla con `TimeoutException`.
**Causa:**
*   La página de SIGGES no cargó correctamente el script de UI.
*   Un modal (ventana emergente) quedó "fantasma" en el DOM.
*   Conexión a internet inestable.
**Solución:**
1.  **Recargar Manual:** Presiona F5 en la ventana de Edge. El script es lo suficientemente inteligente para re-detectar dónde está.
2.  **Verificar Selectores:** Si persiste, es posible que SIGGES haya actualizado su código. Revisa `App/src/utils/Direcciones.py` y confirma que `SPINNER_CSS` coincida con la web real (F12 > Inspector).
3.  **Aumentar Timeouts:** En `mission_config.json`, busca configuraciones de tiempo de espera (si están expuestas) o edita `Driver.py` (buscar `WebDriverWait`).

### 2. Errores de Importación (`ImportError`, `ModuleNotFoundError`)
**Síntoma:** "No module named 'Mision Actual'" o similar al iniciar.
**Causa:** Renombrado de carpetas manual o corrupción de la estructura.
**Solución:**
*   **Estructura Correcta:** Asegúrate de que existan las carpetas `Mision Actual` y `Utilidades` en la raíz.
*   **Espacios en Nombres:** Nozhgess v3.0 maneja espacios, pero versiones antiguas no. Actualiza a la última versión.
*   **Script de Reparación:** Ejecuta `verify_imports.py` (si está disponible) para diagnosticar rutas rotas.

### 3. "La Misión no se actualiza" / "Sigue usando códigos viejos"
**Síntoma:** Cambias un código en el Panel de Control, guardas, pero el script sigue usando la lista anterior.
**Causa:**
*   Caché de Python (`__pycache__`).
*   El botón "Usar Ahora" no escribió correctamente en `mission_config.json`.
**Solución:**
1.  **Forzar Recarga:** En la pestaña "Configuración Web", presiona el botón "Recargar Módulos" (si existe) o reinicia la aplicación GUI.
2.  **Verificar JSON:** Abre `App/config/mission_config.json` con un editor de texto borra la caché manual y verifica que tus cambios estén ahí.

---

## 📋 Diagnóstico Avanzado (Logs)

El sistema genera logs detallados en la carpeta `Logs/`. Aprende a leerlos:

### `terminal_YYYYMMDD.log`
Contiene el resumen ejecutivo. Busca aquí para ver:
*   Cuántos casos se procesaron.
*   Errores fatales (rojo).
*   Resultados finales.

### `debug_YYYYMMDD.log`
Contiene la traza forense. Busca aquí si:
*   El script hizo clic en el lugar equivocado.
*   Se detectó un texto incorrecto.
*   Necesitas ver los tiempos de respuesta del servidor en milisegundos.
*   **Clave de búsqueda:** Busca "❌" para errores o "⚠️" para advertencias.

---

## 🚑 Procedimiento de Emergencia (Reset Total)

Si la aplicación está en un estado irrecuperable:

1.  Cierra todas las ventanas de **Nozhgess** y **Microsoft Edge**.
2.  Ve a la carpeta `App/__pycache__` y bórrala.
3.  Ve a `App/src/core/__pycache__` y bórrala.
4.  Ejecuta `INICIAR_NOZHGESS.bat` nuevamente.

Esto fuerza una recompilación limpia de todo el código Python y reinicia los estados de memoria.

---

## 📞 Soporte

Si el problema persiste tras seguir estos pasos:
1.  Recopila el último archivo de la carpeta `Logs/Debug`.
2.  Toma una captura de pantalla del error en la GUI.
3.  Envía el reporte al equipo de desarrollo (**Nozhtrash**).
