# 🖥️ DOCUMENTACIÓN FRONTEND PROFUNDA: LA CARA DIGITAL

> **Propósito:** Manual de arquitectura de interfaz (GUI) y Sistema de Diseño.
> **Alcance:** `App/src/gui`, `theme.py` y manejo de Hilos.
> **Estética:** Premium Dark Mode (Hardcoded).

---

# 1. EL MOTOR DE TEMA (`theme.py`)

Nozhgess no usa colores al azar. Usa un sistema de diseño estricto definido en `App/src/gui/theme.py`.

## 1.1. ADN de Colores (Hex Codes Reales)
Si vas a agregar un botón, USA ESTOS CÓDIGOS. No inventes colores.

| Variable | Código Hex | Uso |
| :--- | :--- | :--- |
| **`bg_primary`** | `#0c0d11` | Fondo principal (Casi negro, toque azulado). |
| **`bg_card`** | `#181d27` | Paneles y tarjetas. Ligeramente más claro. |
| **`accent`** | `#7c4dff` | **Deep Purple**. El color de la marca. Usar en botones primarios. |
| **`success`** | `#4ade80` | Verde neón suave. Para mensajes de "Éxito". |
| **`error`** | `#f87171` | Rojo pastel. Para errores fatales. |
| **`text_primary`** | `#f4f6fb` | Blanco hueso. Texto principal. |
| **`text_muted`** | `#6f7690` | Gris azulado. Texto secundario o logs viejos. |

## 1.2. Tipografía e Iconografía
*   **Fuente:** `Segoe UI`. (Windows Native).
*   **Razón:** Es la única que renderiza Emojis de color (🔥, ✅) correctamente en CustomTkinter sin convertirlos en wireframes blanco y negro.
*   **Tamaños:** `base`=12, `lg`=14, `xl`=16.

---

# 2. ARQUITECTURA DE VISTAS (SPA - Single Page Application)

La aplicación usa un contenedor principal (`app.py`) que intercambia "Vistas" (Frames) en el área central.

## 2.1. El `RunnerView` (`views/runner.py`)
Es el corazón de la operación.
*   **Layout:** Grid de 2 columnas (Panel Control Izq / Consola Der).
*   **Componente Clave:** `LogConsole`. No es un Textbox normal.
    *   Tiene **Autoscroll Inteligente**: Si subes con la rueda, se pausa. Si bajas al fondo, se reactiva.
    *   Tiene **Buffer Limitado**: Borra las líneas viejas si pasa de 5000 para no comer RAM.

---

# 3. EL PUENTE DE HILOS (THREADING BRIDGE)

Cómo logra la GUI no congelarse mientras el robot navega.

## 3.1. El Problema "Not Responding"
Selenium bloquea. Si llamas a `driver.get()` en el hilo principal de la GUI, la ventana se congela en blanco ("No responde") hasta que la web cargue.

## 3.2. La Solución: Cola de Mensajes (Queue)
Implementación en `runner.py`:

1.  **Orquestador (`RunnerView._start_execution`):**
    *   Crea un `threading.Thread` (Hilo Robot).
    *   Este hilo ejecuta `Conexiones.ejecutar_revision`.

2.  **El Tubo (`queue.Queue`):**
    *   El Hilo Robot NO TOCA LA GUI.
    *   Llama a `log_queue.put(("Hola", "INFO"))`.

3.  **El Consumidor (`RunnerView._drain_ui_queue`):**
    *   Una función en el Hilo Principal corre cada 100ms (`after(100, ...)`).
    *   Vacía la cola y actualiza los Textbox.

**Regla de Oro:** JAMÁS modificar `self.label_texto` desde dentro de `Driver.py`. Usar siempre el sistema de logs.

---

# 4. SOLUCIÓN DE PROBLEMAS GRÁFICOS

### Caso A: "Los emojis se ven como cuadros vacíos o B/N"
*   **Causa:** Se cambió la fuente en `theme.py` a algo que no es `Segoe UI` (ej: `Arial` o `Roboto`).
*   **Solución:** Restaurar `TYPOGRAPHY["font_family"]["primary"] = "Segoe UI"`.

### Caso B: "La consola parpadea mucho"
*   **Causa:** Exceso de velocidad en el `_drain_ui_queue`.
*   **Solución:** Aumentar el tiempo de `after(50, ...)` a `after(100, ...)`.

### Caso C: "Error: main thread is not in main loop"
*   **Causa:** Alguien intentó abrir un `messagebox` desde el hilo del robot.
*   **Solución:** Usar `log_error` para avisar, no popups bloqueantes.

---
**Diseño System verificado para Alta Densidad de Información.**
