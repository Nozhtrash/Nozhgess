# Historial de Parches y Correcciones (`Historial_Parches.md`)

## 📌 Propósito
Entender por qué el código es como es. Muchas líneas "raras" son cicatrices de batallas pasadas.

## 🐛 Grandes Hitos de Bugs

### 1. El Bug "Sin Caso" (Enero 2026) -> [SOLUCIONADO]
*   **Síntoma**: El robot veía 4 casos pero decía "Sin caso".
*   **Causa**: Al guardar desde la GUI nueva, las keywords se guardaban como `["['Cáncer']"]` (doble string).
*   **Parche**: Se implementó sanitización agresiva en el Panel de Control y validación en `Conexiones.py`.

### 2. El Loop Infinito de Búsqueda (Enero 2026) -> [SOLUCIONADO]
*   **Síntoma**: El robot entraba a búsqueda, salía, y volvía a entrar eternamente.
*   **Causa**: La función `asegurar_en_busqueda` se llamaba a sí misma recursivamente por un error en la lógica de navegación fallback.
*   **Parche**: Se eliminó la recursión y se simplificó la navegación a URL directa.

### 3. "ModuleNotFoundError: src" (Diciembre 2025) -> [SOLUCIONADO]
*   **Síntoma**: El script no iniciaba desde la carpeta raíz.
*   **Causa**: Python no encontraba la carpeta `App` en el path.
*   **Parche**: `Iniciador Script.py` ahora inyecta dinámicamente `os.path.join(root, 'App')` al `sys.path`.

## 🛠️ Evolución del Código

### v1.0 (Legacy)
*   Todo en un solo archivo gigante.
*   Uso de `time.sleep(10)` para todo.

### v2.0 (Modularización)
*   Separación en `Driver`, `Conexiones`, `Mision`.
*   Introducción de `WebDriverWait` (esperas inteligentes).

### v3.0 (GUI Moderna)
*   Panel de Control en CustomTkinter (`App/src/gui`).
*   Intento de "Arquitectura Limpia" (que resultó en el lío de `enhanced_app.py` vs `app.py`).

## 🔮 Lecciones Aprendidas
*   **Nunca confiar en el Input del Usuario**: Lo que pegan en el Excel o en la GUI siempre trae basura oculta.
*   **Si algo funciona, NO LO TOQUES**: Especialmente los XPaths de `Direcciones.py`. Un cambio "limpio" puede romper la detección en casos borde.
