# Validaciones y Seguridad (`Validaciones.py`)

## 📌 Propósito y Definición
Este módulo es el "Portero de Discoteca" del script.
Su trabajo es dudar de todo: ¿Es ese string realmente un RUT válido? ¿Ese botón es clickeable o está tapado por un banner? ¿La fecha "32/01/2026" existe?

## ⚙️ Validaciones de Datos

### `validar_rut(rut)` -> `(bool, str)`
*   **Qué hace**: Valida formato y Dígito Verificador (Módulo 11).
*   **Normalización**: Retorna el RUT limpio (sin puntos, con guión, mayúscula) si es válido.
*   **Uso**: Cada vez que se lee un RUT de la web o del Excel.

### `validar_fecha(fecha)`
*   **Paranoia**: No acepta "31/02/2025". Usa `datetime` real.
*   **Rango**: Falla si el año es menor a 1900 o mayor a 2100 (evita errores de tipeo "20225").

## 🛡️ Validaciones de Selenium (Anti-Flakes)

### `elemento_realmente_visible(e)`
*   Mucho más estricto que el `is_displayed()` nativo.
*   **Verificaciones extra**:
    *   Tamaño > 0 (width/height).
    *   Ubicación dentro del viewport (x > -100).
    *   No transparente (opcionalmente).
*   **Por qué**: SIGGES a veces renderiza popups ocultos que Selenium "ve" pero el usuario no. Clickearesos rompe el script.

### `validar_texto_elemento(e)`
*   **Problema**: A veces el texto carga progresivamente ("Car..." -> "Cargando").
*   **Solución**: Lee el texto, espera 100ms, y lo lee de nuevo. Si coindicen, retorna. Si no, asume inestabilidad.

## ⚠️ Filosofía "Defensive Coding"
Todas las funciones retornan una **Tupla** `(Exito, Valor)`.
Esto obliga al código cliente a verificar el éxito antes de usar el valor:
```python
ok, rut = validar_rut(texto)
if not ok:
    raise ValueError("RUT inválido")
```
