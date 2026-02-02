# 🗺️ MAPA DE DATOS Y SELECTORES: LA CARTOGRAFÍA DE NOZHGESS

> **Propósito:** Guía de calibración y mapeo de datos.
> **Fuente de Verdad:** `App/src/core/locators.py` y `mission_config.json`.
> **Uso:** Referencia obligatoria para reparar "Drift" (Cambios en la web).

---

# 1. EL DICCIONARIO DE SELECTORES (`locators.py`)

Nozhgess usa un sistema de claves constantes para referirse a elementos cambiantes.

## 1.1. Tabla de Claves Maestras
Si SIGGES cambia, actaulice el XPath asociado a estas claves.

| Clave Interna | Descripción | XPath Actual (Ref) |
| :--- | :--- | :--- |
| **`LOGIN_BTN_INGRESAR`** | Botón Login | `/html/body/div/div/div[2]/div[1]/form/div[3]/button` |
| **`INPUT_RUT`** | Campo de texto RUT | `//*[@id='rutInput']` |
| **`BTN_BUSCAR`** | Lupa de búsqueda | `#root > ... > button` |
| **`MINI_TABLA_TBODY`** | Tabla resumen casos | `.../div[2]/div/div/table/tbody` |
| **`TABLA_PROVISORIA_TBODY`** | Tabla fechas caso | `.../div[3]/div/table/tbody` |
| **`CHK_HITOS_GES`** | Checkbox desplegar | `.../input[type=checkbox]` |

---

# 2. MAPA DE EXTRACCIÓN DE DATOS (SCRAPING)

Qué columna HTML alimenta qué variable del reporte.

## 2.1. Tabla Información del Paciente
*   **Edad:** Se extrae de `EDAD_PACIENTE`.
    *   *Formato Raw:* "70 Años, 1 Mes, 2 días".
    *   *Procesamiento:* Se corta el string hasta la coma. Queda "70 Años".

## 2.2. Tabla IPD (Informes de Proceso Diagnóstico)
Busca la confirmación médica.
*   **Fuente:** `IPD_TBODY_FALLBACK`
*   **Iteración:** Escanea todas las filas (TR).
*   **Mapeo de Columnas:**
    *   `td[3]` -> **Fecha IPD**.
    *   `td[7]` -> **Confirmación** (Texto clave: "Si").
    *   `td[8]` -> **Diagnóstico**.

## 2.3. Tabla OA (Órdenes de Atención)
Busca exámenes realizados.
*   **Fuente:** `OA_TBODY_FALLBACK`
*   **Mapeo de Columnas:**
    *   `td[1]` -> **Folio** (Usado para cruzar con Prestaciones).
    *   `td[3]` -> **Fecha OA**.
    *   `td[10]` -> **Código Prestación** (Se compara con `habilitantes` del JSON).
    *   `td[13]` -> **Nombre Examen**.

## 2.4. Tabla Cierre GES
Detecta por qué se cerró un caso.
*   **Fuente:** `CIERRE_GES_TBODY`
*   **Mapeo de Columnas:**
    *   `td[3]` -> **Fecha Cierre**.
    *   `td[8]` -> **Subcausal** (Texto largo explicativo).

---

# 3. LÓGICA DE NEGOCIO Y EXCEL (`mission_config.json`)

El archivo JSON define cómo se interpreta lo extraído.

## 3.1. Habilitantes (Alertas Rojas)
*   **Definición:** `config["habilitantes"]`. Lista de códigos (ej: `["5002101"]`).
*   **Lógica:** Si `OA_CODIGO` (td[10]) == `5002101` ->
    1.  Crear Columna en Excel con nombre del examen.
    2.  Pintar celda ROJA.
    3.  Escribir FECHA del examen.

## 3.2. Excluyentes (Falsos Positivos)
*   **Definición:** `config["excluyentes"]`.
*   **Lógica:** Si encuentra este código, el paciente se descarta o se marca en AZUL CLARO. Intencionado para diferenciar patologías similares (ej: Diabetes 1 vs 2).

## 3.3. Índices de Entrada
Si el Excel de entrada (la Misión) cambia, el robot no sabrá cuál celda es el RUT.
*   `"rut": 1` -> Columna B.
*   `"nombre": 3` -> Columna D.
*   **Fix:** Si Sistemas cambia el reporte, editar estos números en el JSON.

---

# 4. GUÍA DE REPARACIÓN DE SELECTORES

**Síntoma:** "El Excel dice 'Sin Info' en Fecha IPD, pero en la web SÍ sale fecha".
**Causa:** SIGGES agregó una columna nueva a la izquierda, desplazando todo.

**Protocolo de Reparación:**
1.  Abrir SIGGES en Chrome/Edge.
2.  Ir a la tabla IPD.
3.  Click derecho en la Fecha -> "Inspeccionar".
4.  Contar los `<td>` anteriores. ¿Son 3 o 4?
5.  Si ahora es el 4º, ir a `App/src/core/locators.py`.
6.  Buscar `IPD_FECHA`.
7.  Cambiar `.../td[3]` por `.../td[4]`.
8.  Guardar. **No requiere recompilar.**

---
**Mapa actualizado a la estructura HTML vigente a Febrero 2026.**
