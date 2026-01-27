# Sistema de Selectores (`Direcciones.py`)

## 📌 Propósito y Definición
Este archivo centraliza **TODOS** los XPaths del proyecto.
El código principal (Driver, Conexiones) **NUNCA** debe contener un string hardcodeado como `//div[@class='foo']`. Todo debe referenciarse desde aquí.

## ⚙️ Arquitectura de Fallbacks
Este archivo no devuelve un solo XPath, sino **LISTAS de XPaths** para cada elemento.
El Driver está programado para iterar sobre esta lista hasta encontrar uno que funcione.

### Ejemplo: Botón Ingresar
```python
"LOGIN_BTN_INGRESAR": [
    "//button[.//p[normalize-space()='Ingresar']]",  # Prioridad 1: Texto exacto
    "//button[@type='submit'...]",                   # Prioridad 2: Atributos
    "/html/body/...",                                 # Prioridad 3: Ruta absoluta (frágil)
]
```
Esta estrategia permite que el script sobreviva a rediseños menores de SIGGES (ej: cambiaron la clase CSS pero el texto sigue diciendo "Ingresar").

## 🗺️ Mapa de Elementos Críticos

### 1. Detección de Estado (`detectar_estado_actual`)
El Driver usa estos selectores para saber dónde está:
*   **Login**: Identificado por `LOGIN_BTN_INGRESAR`.
*   **Búsqueda**: Identificado por `INPUT_RUT`.
*   **Cartola**: Identificado por `CONT_HITOS_GES` (checkboxes de filtros).

### 2. Mini Tabla (`MINI_TABLA_TBODY`)
Es el elemento más difícil de detectar porque a veces carga vacío.
*   **Estrategia**: Prioriza un `tbody` que contenga `tr` con `td` (filas con datos). Si encuentra un tbody vacío, lo ignora en la primera pasada para dar tiempo a que carguen los datos.

### 3. Fallbacks de Tablas Clínicas (IPD, OA, APS)
Debido a que todas las tablas en SIGGES se parecen (clases genéricas `cardTable`), se usan selectores basados en **Texto del Encabezado**:
*   Busca un `p` que diga "Informes de Proceso" y luego busca la tabla adyacente.
*   Esto evita confundir la tabla de APS con la de IPD.

## ⚠️ Debilidades y Puntos de Falla (Honestidad Brutal)
1.  **Selectores Absolutos**: Algunas entradas (especialmente las añadidas por parches rápidos) usan `/html/body/div/main...`. Estos son **BOMBAS DE TIEMPO**. Cualquier cambio en el layout de SIGGES romperá estos selectores.
2.  **Dependencia del DOM**: Nozhgess no usa API (porque no existe pública). Depende 100% de que el HTML no cambie drásticamente.
3.  **Texto Hardcodeado**: Si SIGGES cambia "Buscar RUN" por "Buscar Paciente", la prioridad 1 fallará y dependerá de los fallbacks.

## 📝 Guía de Mantenimiento
Si SIGGES cambia y el robot no encuentra un botón:
1.  Inspeccionar elemento en Chrome/Edge (F12).
2.  Copiar el nuevo XPath.
3.  **AGREGARLO** al inicio de la lista en `Direcciones.py` (no borres los antiguos, déjalos de fallback).
