# ⚖️ ESTÁNDAR DE CÓDIGO Y MANTENIMIENTO
> **"Robustez sobre Velocidad. Verdad sobre Suposición."**
> **Perfil:** Mantenedores, Desarrolladores y Auditores de Software.

Este documento establece las reglas de oro para cualquier persona que desee modificar el motor de Nozhgess. El incumplimiento de estas normas compromete la precisión clínica del sistema.

---

# 1. FILOSOFÍA DE DESARROLLO

1.  **NO ALUCINAR:** Nunca asuma que un elemento está presente. Use siempre `waits.wait_for_element`. Si un dato no existe, devuelva cadena vacía o `None`, jamás invente valores por defecto.
2.  **TIER SSS+ RELIABILITY:** Preferimos que el robot tarde 1 segundo más por paciente a que falle por un cambio de estado en el DOM. El `time.sleep(1.0)` en `core.py` es sagrado.
3.  **EVIDENCIA TANGIBLE:** Cada decisión que tome el motor (ej. marcar un paciente como "Apto Caso") debe estar respaldada por un log que explique el por qué, el cuándo y el dónde.

---

# 2. LAS REGLAS DE ORO DEL MOTOR (CORE)

### 🚀 Selenium & Acciones
- **Prohibido el Click Directo:** No use `element.click()`. Use siempre `self._click(locator)`. La función `_click` implementa scroll táctico, limpieza de caché e inyección de JavaScript de respaldo.
- **XPaths Relativos:** Evite XPaths absolutos (`/html/body/...`). Use atributos estables como `@id`, `@name` o `@class` únicos.
- **Spinners:** Siempre verifique si hay un spinner activo (`dialog.loading`) antes de interactuar.

### 🧵 Concurrencia y Hilos
- **Thread Safety:** Nunca intente modificar la UI (Labels, Buttons) desde `Conexiones.py` o `Driver.py`. Use el sistema de `log_queue`.
- **Worker Isolation:** El hilo trabajador no debe conocer la existencia de `CustomTkinter`. Debe ser puro Python/Selenium.

### 🛡️ Gestión de Errores (Forensic)
- **Catch Específico:** Evite `try: ... except Exception:`. Capture errores específicos (ej. `TimeoutException`, `NoSuchElementException`).
- **Detección Fatal:** Si una excepción indica pérdida de sesión, use `es_conexion_fatal()` para cerrar el proceso de forma segura.

---

# 3. ESTÁNDAR DE LOGS

Los logs deben seguir este formato para ser legibles en la consola premium:

- `[DEBUG]`: Trazas técnicas de bajo nivel (Selectores, tiempos).
- `[INFO]`: Progreso general (Ej: "Procesando paciente 5/100").
- `🔥 [SUCCESS]`: Hitos completados (Ej: "Caso en Contra encontrado").
- `⚠️ [WARN]`: Datos faltantes pero no críticos (Ej: "Sin fecha IPD").
- `❌ [ERROR]`: Fallos que detienen el procesamiento de un paciente.

---

# 4. MANTENIMIENTO DEL "MAPA DE DATOS"

Cuando SIGGES cambie:
1.  Actualice primero `locators.py`.
2.  Verifique la lógica en `Conexiones.py`.
3.  Actualice el manual `DOCUMENTACION_MAPA_DE_DATOS.md` para reflejar el cambio.

> **Regla de Cierre:** "Si el código no está documentado en la Biblia Técnica, no existe."

---

**© 2026 Nozhgess Engineering Council**
*"La robustez no es un accidente, es el resultado de un estándar estricto."*
