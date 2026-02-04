# Plan de Refactorización: Unificando la Arquitectura Híbrida

## 1. El Diagnóstico: "El Problema de los Dos Cerebros"
El proyecto Nozhgess actualmente opera con dos cerebros distintos unidos por un puente frágil:

1.  **Cerebro Legacy (`Utilidades/`)**: Basado en scripts secuenciales, variables globales (`Mision_Actual.py`) y ejecución lineal. Es potente y contiene toda la lógica de negocio actual.
2.  **Cerebro Moderno (`App/`)**: Basado en Clases, Orientación a Objetos, Interfaz Gráfica (`customtkinter`) y configuración JSON.

**La Fragilidad:**
El sistema depende de archivos puente (`Nozhgess.pyw`, `MisionController`) para mantener estos dos mundos sincronizados.
- Si la GUI cambia una configuración, debe escribir un archivo JSON *Y* forzar la recarga de un módulo Python global. Si este proceso falla, el backend ejecuta con datos viejos.
- El uso de `sys.path.insert` hace que mover carpetas rompa imports.

## 2. La Solución: "Transfusión de Arquitectura"
El objetivo es migrar la lógica (sangre) del sistema legacy al cuerpo moderno (`App/`), eliminando la dependencia de `Utilidades/`.

### Fase 1: Encapsulamiento (Menor Riesgo)
En lugar de que `Conexiones.py` lea variables globales (`from Mision_Actual import...`), debemos convertirlo en una función que **reciba** la configuración.

**Actual:**
```python
# Conexiones.py
from Mision_Actual import NOMBRE_DE_LA_MISION
def analizar_mision():
    print(NOMBRE_DE_LA_MISION)
```

**Meta Fase 1:**
```python
# Conexiones.py refactorizado
def analizar_mision(config: dict):
    print(config["nombre"])
```
*Esto permite llamar al backend desde la GUI pasando el JSON directamente, sin escribir archivos intermedios.*

### Fase 2: Modularización dentro de `App/`
Mover la lógica lógica de `Conexiones.py` a `App/src/engine/`.

1.  Crear `App/src/engine/mission_runner.py`.
2.  Crear `App/src/engine/excel_reporter.py`.
3.  Crear `App/src/engine/scrapers/sigges_scraper.py`.

De esta forma, `Conexiones.py` (de 1600 líneas) se divide en 3 componentes mantenibles.

### Fase 3: Eliminación de `Utilidades`
Una vez que la GUI llame directamente a `App/src/engine/mission_runner.py`:
1.  Se elimina `Mision_Actual.py` (ya no se necesitan variables globales).
2.  Se elimina la carpeta `Utilidades` (el código ya vive en `App`).
3.  `Nozhgess.pyw` se simplifica a un iniciador de la GUI.

## 3. Soluciones Inmediatas (Quick Wins)

### A. Dependencias (`requirements.txt`)
**Problema:** Tienes dos archivos conflictivos.
**Solución:**
1.  Crear un único `requirements.txt` en la raíz.
2.  Contenido unificado:
    ```
    customtkinter>=5.2.0
    pandas>=2.0.0
    openpyxl>=3.1.0
    selenium>=4.10.0
    colorama>=0.4.6
    webdriver-manager>=4.0.0
    ```
3.  Borrar los `requirements.txt` dentro de `App/` y `Utilidades/`.

### B. Rutas Hardcodeadas
**Problema:** `C:/Users/usuariohgf/...`
**Solución:** Usar rutas relativas o variables de entorno.

**Código sugerido:**
```python
import os
USER_HOME = os.path.expanduser("~")
RUTA_SALIDA = os.path.join(USER_HOME, "Documents", "Nozhgess_Salida")
```
Esto funcionará automáticamente en la computadora de `knoth`, `usuariohgf` o cualquier otra.

## 4. Hoja de Ruta Sugerida
1.  **Limpieza (Completado):** Archivos basura removidos.
2.  **Unificar Requerimientos:** Crear un solo `requirements.txt`.
3.  **Fase 1 Refactor:** Modificar `Conexiones.py` para aceptar argumentos (dict) en `procesar_paciente`.
4.  **Fase 2 Migración:** Mover lógica a `App/src`.
