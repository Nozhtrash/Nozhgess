# Anatomía del Sistema Nozhgess: "La Caja Negra" Revelada (`Phase 12`)

> **⚠ ADVERTENCIA CRÍTICA PARA DESARROLLADORES FUTUROS:**
> Este documento describe la estructura **EXACTA** del sistema al momento de su funcionamiento perfecto (Enero 2026).
> Si vas a modificar `Esperas.py` o `Direcciones.py`, **LEE ESTO PRIMERO**. Cualquier cambio en los timings listados aquí puede romper la sincronización con SIGGES.

---

## ⏱️ 1. El Pulso del Sistema (`Esperas.py`)
El sistema no usa `time.sleep()` al azar. Usa un diccionario centralizado de "latidos".
Romper este ritmo causa desincronización (ElementNotInteractable) o bloqueos (SpinnerStuck).

### Tier SSS+ (Operaciones Críticas de < 0.2s)
Estas esperas son agresivas para velocidad máxima. **NO AUMENTAR** salvo emergencia.

| Clave Wait | Tiempo | Descripción | Riesgo de Cambio |
| :--- | :--- | :--- | :--- |
| `nav_a_busqueda_fast` | **0.05s** | Chequeo instantáneo de si estamos en página búsqueda. | Sistema se vuelve lento. |
| `busqueda_nav` | **0.2s** | Navegación directa entre pacientes. | Pérdida de agilidad en bucles largos. |
| `cartola_click_ir` | **0.2s** | Click en botón "Ir a Cartola" tras selección. | Spinner infinito por doble click. |

### Tier A (Estabilidad Funcional)
Tiempos calibrados para la lentitud nativa de SIGGES.

| Clave Wait | Tiempo | Descripción | Por qué existe |
| :--- | :--- | :--- | :--- |
| `search_wait_results` | **8.0s** | Espera a que la tabla aparezca tras buscar RUT. | SIGGES es lento buscando RUTs antiguos. |
| `mini_find_table` | **10.0s** | Encontrar la Mini-Tabla de resultados. | A veces el DOM carga vacío primero. |
| `login_click_ingresar` | **5.0s** | Login inicial. | El servidor de Auth suele tardar. |

---

## 🗺️ 2. El Mapa de Selectores (`Direcciones.py`)
SIGGES es hostil con los selectores. Usamos una estrategia de **"Fallbacks en Cascada"**.
Si el XPATH principal falla, el sistema intenta automáticamente el siguiente.

### Botones Críticos
*   **Ir a Cartola Unificada**:
    *   `Priority 1`: `//button[@id='btnIrCartola']` (ID directo, si existe).
    *   `Priority 2`: `//button[contains(., 'Ir a Cartola')]` (Texto visible).
*   **Buscar Paciente**:
    *   `Priority 1`: `//button[@class='botonBase botonStand2']` (Clase específica).
    *   `Priority 2`: `//button[contains(., 'Buscar')]` (Texto).

### Tablas Clínicas (Estructura DOM)
Las tablas (IPD, OA, APS) están anidadas en `divs` genéricos. Las detectamos por su **Label Hermano**:
*   **Estrategia**: "Busca el texto 'Hoja Diaria APS', sube al padre, busca el siguiente `div` hermano, entra a la `table`".
*   **XPath Maestro**: `//div[label/p[contains(., 'TEXTO_TABLA')]]/following-sibling::div//table/tbody`

---

## 🧠 3. Flujo Vital (`Conexiones.py`)
Este es el algoritmo de decisión exacto que ejecuta `procesar_paciente`.

1.  **Normalización**: RUT sin puntos, fecha standard.
2.  **Búsqueda**:
    *   Navega a `/busqueda-de-paciente`.
    *   Inyecta RUT en `#rutInput`.
    *   Click `Buscar`.
    *   **Checkpoint**: ¿Apareció la Mini-Tabla? (Si no -> `Retry`).
3.  **Selección de Caso (Inteligencia)**:
    *   Lee todos los casos de la Mini-Tabla.
    *   **Puntaje**: `(EstadoActivo * 10^10) + TimestampMasReciente`.
    *   Elige el caso ganador y extrae su `Indice`.
4.  **Extracción Profunda (Cartola)**:
    *   Expande el caso (`Click Checkbox`).
    *   Busca tablas: `IPD` -> `OA` -> `APS` -> `SIC`.
    *   Aplica **Inteligencia de Negocio** (Verificar `Apto SE`, `Apto RE`).
5.  **Cierre**:
    *   Colapsa el caso para liberar memoria DOM.
    *   Reporta resultado a Excel.

---

## 🛡️ 4. Sistema de Seguridad (`Errores.py`)
Cómo el sistema se protege de sí mismo.

### Circuit Breaker
Si una operación falla **3 veces consecutivas** en el mismo paciente:
1.  Lanza `CircuitBreakerError`.
2.  Salta al siguiente paciente.
3.  No detiene el script global (salvo error de conexión).

### Spinner Anti-Stuck
Si el spinner de carga (`dialog.loading`) permanece visible por más de **60 segundos** (`spinner_stuck`):
1.  El sistema asume "Soft Lock".
2.  Fuerza un `driver.refresh()`.
3.  Reinicia el flujo del paciente actual desde cero.

---
*Documento generado para preservación histórica. Enero 2026.*
