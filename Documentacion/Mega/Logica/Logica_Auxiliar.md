# Lógica Auxiliar y Formatos (`Formatos.py`)

## 📌 Propósito y Definición
Este módulo actúa como el "Conserje" de los datos.
SIGGES es un sistema sucio: devuelve textos con espacios extra, fechas en formatos bizarros ("2026-01-01 00:00:00.000"), y nombres con tildes inconsistentes.
`Formatos.py` limpia todo antes de que entre a la lógica de negocio.

## 🧹 Funciones de Limpieza (Sanitización)

### 1. `_norm(texto)`
La función más usada del proyecto.
*   **Qué hace**: `HÓLA MUNDO ` -> `hola mundo`.
*   **Cómo**:
    1.  Descompone caracteres Unicode (NFD).
    2.  Elimina tildes (combining characters).
    3.  Convierte a minúsculas.
    4.  Reemplaza saltos de línea y tabs por espacios simples.
    5.  Elimina caracteres no alfanuméricos (excepto espacios).
*   **Por qué**: Para que "Depresión" sea igual a "DEPRESION" o "depresion".

### 2. `solo_fecha(x)`
El formateador universal de fechas.
*   **Input**: Acepta `datetime`, `str` ("YYYY/MM/DD", "DD-MM-YYYY").
*   **Output**: Siempre devuelve `DD/MM/YYYY` (string).
*   **Clave**: Si recibe basura, devuelve string vacío `""` (no falla).

### 3. `join_clean(lista)`
Une listas de strings para el Excel final.
*   **Filtra**: Vacíos, `None`, y valores "NO TIENE" o "X".
*   **Separador**: Usa `|` para que en Excel no se rompa la celda.

## 🧮 Lógica de Negocio (Fechas)

### `en_vigencia(fecha_nomina, fecha_prestacion, ventana)`
Calcula si una prestación "vale" o es muy antigua.
*   Matemática: `0 <= (Fecha_Nomina - Fecha_Prestacion).days <= Ventana`.
*   **Importante**: Si la prestación es *futura* (negativo), devuelve False (a menos que se cambie la lógica).

## ⚠️ Debilidades y Puntos de Falla
1.  **Regex Fragilidad**: `normalizar_codigo` elimina todo lo que no sea dígito. Si SIGGES introduce códigos alfanuméricos (ej: "A123"), esta función los romperá ("123") y podría causar colisiones.
2.  **Fechas Ambiguas**: El parser intenta adivinar si es `DD/MM` o `YYYY/MM`. Si llega `01/02/03`, asume orden estándar, pero podría equivocarse en formatos mixtos norteamericanos/europeos si la configuración regional del servidor cambia.
