# 📜 BIBLIA TÉCNICA NOZHGESS v2.0

> **Versión:** 2.0 (Edición "Nuclear")
> **Última Actualización:** 02/Feb/2026
> **Autor:** Equipo de Desarrollo Deepmind (Simulado) & Usuario
> **Estado:** PRODUCCIÓN ESTABLE

---

# 📑 ÍNDICE MAESTRO

**📚 Documentación Especializada (Anexos):**
*   [🛠️ DEEP DIVE BACKEND (Reparación de Lógica)](file:///DOCUMENTACION_BACKEND_DEEP_DIVE.md)
*   [🖥️ DEEP DIVE FRONTEND (Arquitectura GUI)](file:///DOCUMENTACION_FRONTEND_PROFUNDA.md)
*   [🗺️ MAPA DE DATOS (Selectores y Excel)](file:///DOCUMENTACION_MAPA_DE_DATOS.md)
1.  [Filosofía del Proyecto](#1-filosofía-y-propósito)
2.  [Arquitectura de Software](#2-arquitectura-de-software-holística)
3.  [Anatomía del Proyecto (Estructura de Carpetas)](#3-anatomía-del-proyecto)
4.  [El Motor "Nuclear" (Core Logic)](#4-el-motor-nuclear-core-logic)
5.  [Sistema de Logs y Telemetría](#5-sistema-de-logs-y-telemetría)
6.  [Mantenimiento de Emergencia](#6-mantenimiento-de-emergencia)

---

# 1. FILOSOFÍA Y PROPÓSITO

**"Robustez sobre Velocidad. Verdad sobre Suposición."**

Nozhgess es un autómata de revisión clínica para la plataforma SIGGES. Su propósito no es solo "hacer clicks", sino "entender" estados médicos complejos para generar reportes en Excel con cero margen de error.

### Principios Fundamentales:
1.  **TIER SSS+ Reliability:** El robot duerme 1.0s obligatoriamente antes de cada acción crítica. Preferimos tardar 10 minutos más que entregar un reporte falso.
2.  **No-Hallucination:** Si un dato no está en la pantalla, el robot dice "No Encontrado", jamás inventa fechas.
3.  **Transparencia Radical:** El usuario ve todo. Si el robot duda, avisa.

---

# 2. ARQUITECTURA DE SOFTWARE HOLÍSTICA

El sistema sigue el patrón **MVC-S** (Model - View - Controller - Service).

*   **VIEW (Frontend):** CustomTkinter (`App/src/gui`). Maneja la interacción humana.
*   **CONTROLLER (Orquestador):** `runner.py`. Gestiona los hilos y colas de mensajes.
*   **SERVICE (Backend):** `Conexiones.py` y `Driver.py`. Interactúan con el mundo exterior (SIGGES).
*   **MODEL (Data):** JSONs de configuración (`mission_config.json`).

### Diagrama de Comunicación:
```
[GUI Thread] <--(Queue 100ms)--> [Worker Thread] <--(HTTP/9222)--> [Edge Driver] <--> [SIGGES Web]
```

---

# 3. ANATOMÍA DEL PROYECTO

Estructura física real en disco.

```text
Nozhgess original/
├── App/
│   ├── config/              # Cerebro configurable
│   │   └── mission_config.json  # Define reglas de negocio (Diabetes, HTA, etc)
│   ├── src/
│   │   ├── core/            # El Motor
│   │   │   ├── Driver.py        # Wrapper Selenium
│   │   │   ├── locators.py      # Diccionario de Direcciones (La Biblia)
│   │   │   └── modules/core.py  # Lógica base (Clicks nucleares)
│   │   ├── gui/             # La Cara
│   │   │   ├── app.py           # Main Loop
│   │   │   ├── theme.py         # Sistema de Diseño y Hex Codes
│   │   │   └── views/runner.py  # Panel de Control
│   │   └── utils/           # Herramientas
│   │       └── Excel_Revision.py # Generador de Reportes
│   └── themes/              # JSONs de estilos visuales
├── Documentacion/           # Biblioteca de Alejandría
├── Iniciador/
│   └── Iniciador Web.ps1    # Script de PowerShell vital (Puerto 9222)
└── Nozhgess.pyw             # Gatillo de ejecución (Doble click aquí)
```

---

# 4. EL MOTOR "NUCLEAR" (CORE LOGIC)

Aquí residen las innovaciones técnicas que diferencian a Nozhgess de un script básico.

## 4.1. El Click Atómico (`_click`)
Ubicado en `src/core/modules/core.py`. No es un simple `element.click()`.
Es una secuencia militar:
1.  **Invalidar Caché:** Olvida todo lo que sabía de la página anterior.
2.  **TIER SSS+ Sleep:** `time.sleep(1.0)`. Pausa táctica obligatoria.
3.  **Wait Smart:** Espera a que desaparezca el Spinner (`dialog.loading`).
4.  **Scroll Táctico:** JS `scrollIntoView({block:'center'})`. Centra el objetivo.
5.  **Click:**
    *   Intento 1: Selenium Nativo.
    *   Intento 2: **JavaScript Injection** (`arguments[0].click()`).
6.  **Post-Wait:** Verifica nuevamente si apareció un spinner.

## 4.2. Detector de Fatales (`es_conexion_fatal`)
El robot sabe cuándo rendirse. Si detecta estas strings en una excepción, aborta para no quemar CPU:
*   `no such window`
*   `target window already closed`
*   `connection refused` (El usuario cerró Edge)
*   `session not created` (Versión de Driver incompatible)

## 4.3. Configuración de Misión (`mission_config.json`)
El archivo JSON que define la "personalidad" de la revisión.
*   **`indices`:** `{"rut": 1, "nombre": 3}` -> Mapea columnas del Excel de entrada.
*   **`habilitantes`:** Lista de códigos (ej: `5002101`) que activan alertas rojas.
*   **`DIRECCION_DEBUG_EDGE`:** `localhost:9222` (Invariable).

---

# 5. SISTEMA DE LOGS Y TELEMETRÍA

El "Sistema Nervioso" de la aplicación.

*   **Log de Usuario (Terminal):** Mensajes con Emojis (🔥, ✅, ❌). Amigables.
*   **Log de Debug (Oculto):** Trazas de `[DEBUG] Wait time: 0.23s`. Solo para desarrolladores.
*   **Log en Disco (`Logs/`):** Archivo rotativo. Se guarda todo lo que pasa por si el cliente reclama.

---

# 6. MANTENIMIENTO DE EMERGENCIA

### Caso A: "El Excel sale sin colores"
*   **Culpable:** `Excel_Revision.py`
*   **Solución:** Verificar que las constantes de colores (ej: `COLOR_HEADER_AZUL = "4F81BD"`) no hayan sido modificadas. El script usa nombres internos ("azulP", "verde", "morado") que deben coincidir.

### Caso B: "No encuentra el botón Ingresar"
*   **Culpable:** Cambio en SIGGES o `locators.py` desactualizado.
*   **Solución:** Abrir `locators.py`, buscar `LOGIN_BTN_INGRESAR` y actualizar el XPath usando DevTools (F12).

### Caso C: "Se queda pegado en 'Cargando...'"
*   **Culpable:** `Iniciador Web.ps1`
*   **Solución:** Cerrar todas las ventanas de Edge. Ejecutar el `.ps1` manualmente y ver si tira error en rojo. Verificar puerto 9222.

---
**© 2026 Nozhgess Project.**
*Software de grado clínico - Ingeniería de alta precisión.*
