# 🛠️ DEEP DIVE BACKEND: EL SISTEMA NERVIOSO v3.5.1
> **Audiencia:** Desarrolladores de Sistemas, Expertos en Automatización y Soporte Nivel 3.
> **Propósito:** Documentación forense para la reparación, expansión y auditoría del motor "Nuclear" Integrado.

---

# 1. ANATOMÍA DEL "HOOK" (SESSION PARASITISM V2)

Nozhgess no es un bot que abre un navegador limpio; es un **parásito de sesión**. Se conecta a una instancia de Edge ya abierta y autenticada.

### 1.1. El Protocolo: Chrome DevTools Protocol (CDP)
El motor utiliza el puerto `9222` para enviar comandos JSON directamente al motor Chromium de Edge.
- **Control Remoto:** Hereda cookies, tokens de seguridad (MFA) y certificados Windows sin intervención humana.

### 1.2. El Integrador (`integrator.py`)
Nuevo en v3.5.1, actúa como el orquestador maestro que unifica la lógica legacy (`Conexiones.py`) con las nuevas capacidades avanzadas:
- **`PerformanceOptimizer`:** Gestiona el procesamiento por chunks de memoria y limpieza de caché.
- **`AdvancedProcessor`:** Centraliza la validación de RUTs, nombres y duplicados antes de tocar la red.

---

# 2. ORQUESTACIÓN DE `Conexiones.py` Y EL DRIVER

### 2.1. El Pipeline de Extracción Forense
Cada paciente sigue un ciclo de lectura de sub-tablas mediante `DataParsingMixin`:

1.  **IPD (Informes Diagnósticos):** Busca la confirmación del diagnóstico para el **Apto RE**.
2.  **OA (Órdenes de Atención):** Compara códigos web contra la lista `habilitantes` del JSON.
3.  **SIC (Interconsultas):** Detecta derivaciones especialista para el **Apto SE**.

### 2.2. Detección Inteligente de Casos
`seleccionar_caso_inteligente` utiliza un sistema de pesos:
- `Peso = (EsActivo * 10^10) + (CercaníaNombre * 10^5) + Timestamp`.
Esto garantiza que si hay 10 casos, el robot elija el que tiene más relevancia clínica actual.

---

# 3. GESTIÓN DE FALLOS Y FAIL-SAFE

### 3.1. Detección Fatal y Retry Manager
- **Backoff Exponencial:** Si un elemento falla, el sistema espera (2^intento) segundos antes de reintentar, evitando ser detectado como un ataque de denegación de servicio.
- **`es_conexion_fatal`:** Captura errores de nivel de socket y dispara el cierre preventivo del driver para evitar procesos zombie.

### 3.2. Lógica de Reintentos de Click
Si un click normal falla, Nozhgess aplica:
- `ActionChains(driver).move_to_element(el).click().perform()`
- Fallback: `arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}))` vía JavaScript.

---

# 4. OPTIMIZACIÓN DE DATOS (PANDAS & OPENPYXL)

- **Memory Mapping:** `integrator.py` optimiza los tipos de datos de las columnas (ej. `float64` a `int32`) para reducir el consumo de RAM en un 40%.
- **Secure Logging:** `secure_logging.py` ofusca datos sensibles en los logs pero los mantiene íntegros en la memoria de procesamiento.

---

# 5. TROUBLESHOOTING DE BAJO NIVEL (N3)

### 🚨 "Stale Element Reference Exception"
- **Diagnóstico:** El robot tiene la dirección de un elemento, pero el DOM se refrescó.
- **Solución:** `sigges.reset_state()` forzando la reinvalidación de la mini-tabla de casos.

### 🚨 "Integrator: Chunk Processing Error"
- **Diagnóstico:** El archivo Excel tiene celdas corruptas o fórmulas que Pandas no puede evaluar.
- **Solución:** Abrir Excel, Guardar como... "Libro de Excel (.xlsx)" limpio para eliminar macros viejas.

---

**© 2026 Nozhgess Engineering Team**
*"La robustez es el único estándar aceptable."*

