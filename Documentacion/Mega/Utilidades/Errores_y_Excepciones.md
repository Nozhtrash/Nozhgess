# Gestión de Errores (`Errores.py`)

## 📌 Propósito y Definición
Selenium escupe errores horribles como `selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document`.
Este módulo traduce ese "vómito de código" a algo legible por humanos: `Elemento obsoleto (stale)`.

## ⚙️ Funciones Clave

### `pretty_error(e)`
*   Analiza el string de la excepción.
*   Usa Regex y palabras clave para identificar el problema real.
*   Devuelve un mensaje corto (máx 180 caracteres) para que quepa en el terminal.

### `clasificar_error(e)`
*   Categoriza el error para estadísticas (`timeout`, `not_found`, `stale`).
*   Esto permitiría saber si el 80% de los fallos son por Timeout (Internet lento) o Not Found (Cambio de selectores).

## ⚠️ Debilidades y Puntos de Falla
1.  **Catch-All Genérico**: Si aparece un error nuevo de Selenium 5.0, caerá en categoría `unknown` con un log genérico.
2.  **Sin Stacktrace**: Al "embellecer" el error, ocultamos la línea exacta donde falló. Para debug profundo (`DEBUG_MODE`), esto es una desventaja.
