# 🏗️ Manual de Arquitectura Técnica

Este documento describe la estructura interna del robot Nozhgess, detallando cómo interactúan sus componentes críticos.

---

## 1. Sistema de Logs y Terminales "Trifecta"

La interfaz visual (`runner.py`) implementa un sistema de observabilidad basado en tres canales con responsabilidades estrictas.

### Flujo de Datos
```
[Procesos Internos] --> [Stdout / Print] --> [Runner Capture] --> [Filtro Regex] --> [Terminal Display]
       |
       +--> [Logging Module] --> [Archivo .log] --> [GuiLogHandler] --> [General Display]
```

### Tabla de Ruteo (Runner.py)
El método `_poll_logs` clasifica cada línea de texto basándose en prefijos (emojis o etiquetas):

| Terminal | Fuente | Patrones (Regex/Startswith) | Contenido |
| :--- | :--- | :--- | :--- |
| **🟦 Principal** | Stdout | `🔥` (Header), `📊` (Status), `📋` (Resumen), `🤹🏻` (Nombre), `✅`, `❌` | Información de alto nivel para el usuario final. Limpio. |
| **🟨 Debug** | Stdout | `⏱️` (Timing), `⏳` (Espera), `✓` (Check), `└─` (Traza), `[DEBUG]` | Detalle técnico paso a paso, tiempos de respuesta y flujo interno. |
| **⬜ General** | Archivo | Todo lo que tenga `level="FILE"` | Espejo exacto del archivo de log. Sin filtros. Auditoría total. |

---

## 2. Gestión de Configuraciones (Panel de Control)

El sistema ya no depende de editar código para configurar misiones. Todo se centraliza en `App/config/mission_config.json`.

### Estructura del JSON
```json
{
  "MISSIONS": [
    {
      "nombre": "Cáncer Cervicouterino",
      "keywords": ["Cáncer", "Tumor"],  <-- LISTA PURA DE STRINGS
      "habilitantes": ["0801001", "801101"],
      ...
    }
  ],
  "DIRECCION_DEBUG_EDGE": "localhost:9222"
}
```

### Seguridad en el Input (`control_panel.py`)
Para evitar corrupciones de datos (como el error "Sin Caso" donde se guardaban listas dentro de cadenas), el Panel de Control implementa **Sanitización Activa**:
*   Intercepta cualquier entrada en campos de lista (Keywords, Códigos).
*   Elimina caracteres peligrosos: `[` `]` `'` `"`
*   Asegura que `mission_config.json` siempre tenga JSON válido.

**Clase Clave:** `src.gui.views.control_panel.ControlPanelView` -> `_gather_form_data()`

---

## 3. Arquitectura de Misiones ("Conexiones")

El cerebro de decisión está en `Utilidades/Mezclador/Conexiones.py`.

### Algoritmo de Selección de Caso (`seleccionar_caso_inteligente`)
Cuando el robot lee la "Mini-Tabla" de casos del paciente, decide cuál abrir siguiendo este algoritmo:

1.  **Filtrado por Keywords:** Revisa si el nombre del caso contiene alguna de las palabras clave de la configuración.
    *   *Nota:* Si kws está vacío, pasan todos.
2.  **Scoring (Puntaje):**
    *   Base: `10,000,000,000` puntos si el caso está **ACTIVO**.
    *   Plus: `Timestamp` de la fecha del caso (para preferir el más reciente).
3.  **Selección:** Gana el caso con mayor puntaje.

Esto asegura que el robot siempre prefiera un caso "Abierto" y "Reciente" sobre uno "Cerrado" o "Antiguo", siempre que coincida con el tema (Cáncer, Epilepsia, etc).

---

## 4. Drivers y Navegación

*   **Driver:** `src.core.Driver.py` (Wrapper de Selenium/Playwright).
*   **Conexión Debug:** Se conecta a una instancia de Edge ya abierta (`localhost:9222`) para evitar bloqueos por autenticación 2FA/Clave Única.
*   **Wait Strategy:** Usa esperas explícitas inteligentes (`WebDriverWait`) combinadas con chequeos visuales (spinners).
