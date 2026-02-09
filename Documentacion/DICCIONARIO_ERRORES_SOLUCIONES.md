# 📕 DICCIONARIO MAESTRO DE ERRORES Y SOLUCIONES
> **Versión:** 1.1 (Feb 2026) - Edición Forense III
> **Nivel de Detalle:** Nivel 3 (Soporte & Ingeniería)

Este documento es la referencia definitiva para diagnosticar y reparar Nozhgess. Los errores se clasifican por su origen, severidad y protocolo de resolución.

---

# 1. ERRORES DE INFRAESTRUCTURA (NIVEL ROJO 🔴)
*Impiden el arranque o la conexión con el motor de automatización.*

| Código / Mensaje | Causa Raíz | Solución Técnica N3 |
| :--- | :--- | :--- |
| **`ConnectionRefusedError`** | Puerto 9222 de Edge cerrado o script PS1 no ejecutado. | Cerrar Edge, ejecutar `Iniciador Web.ps1` y verificar puerto con `netstat -ano | findstr 9222`. |
| **`DevToolsActivePort`** | Perfil de Edge bloqueado por otra instancia. | Ejecutar `taskkill /F /IM msedge.exe` y reintentar. |
| **`SessionNotCreated`** | Versión de Edge y Driver desincronizados. | Actualizar `msedgedriver.exe` en `App/bin` (Verificar versión en `edge://settings/help`). |
| **`MaxRetryError`** | Fallo crítico en el `RetryManager` tras 5 intentos. | Reiniciar el equipo. Indica saturación de memoria o hilos huérfanos. |

---

# 2. ERRORES DEL MOTOR DE AUTOMATIZACIÓN (NIVEL NARANJA 🟠)
*El robot está corriendo, pero falla en la interacción con la web.*

| Código / Mensaje | Causa Raíz | Protocolo de Resolución |
| :--- | :--- | :--- |
| **`TimeoutException`** | Elemento no cargó en el tiempo estipulado (Default 10s). | Aumentar `ESPERA_MEDIO` en `src/utils/Esperas.py` o verificar latencia de red. |
| **`ClickIntercepted`** | Un popup o el "Spinner" de SIGGES bloquea el elemento. | Verificar que `SPINNER_CSS` en `locators.py` esté actualizado (SIGGES cambia IDs frecuentemente). |
| **`StaleElement`** | El DOM cambió mientras se leía el dato. | El sistema ya reintenta, pero si persiste, forzar `sigges.refresh()` antes de la lectura. |
| **`ElementNotInteractable`** | El elemento existe pero está oculto o deshabilitado. | Verificar si el paciente está en estado "Cerrado" o "Anulado" en SIGGES. |

---

# 3. ERRORES DE LÓGICA CLÍNICA Y DATOS (NIVEL AMARILLO 🟡)
*El robot termina, pero los resultados requieren auditoría humana.*

### 3.1. Caso en Contra / Alerta de Divergencia
- **Síntoma:** El Excel marca "Caso en Contra" y bloquea el procesamiento automático.
- **Causa:** El paciente tiene una patología GES distinta a la proyectada en la misión (Ej: T1 vs T2).
- **Solución:** Nozhgess extrae los datos del caso divergente. El auditor debe validar si el ingreso en la nómina original fue un error administrativo.

### 3.2. Disparidad de Códigos de Prestación
- **Síntoma:** El reporte dice "No Encontrado" pero el examen está en SIGGES.
- **Solución:** SIGGES usa espacios al final de los códigos. Nozhgess v3.5.1 usa `Formatos.normalizar_codigo()` para limpiar estos caracteres. Verifique que el código en el JSON no tenga caracteres ocultos.

---

# 4. PROTOCOLO DE SOPORTE AVANZADO

Si el error persiste tras aplicar las soluciones:
1.  **Auditoría de Logs:** Revise `Logs/latest.log`. Busque la traza `[TERMINAL]` para errores de lógica o `[DEBUG]` para errores de Selenium.
2.  **Volcado Forense:** Si un RUT falla sistemáticamente, el sistema genera un `debug_root_RUT.html`. Ábralo para ver qué leyó el robot.
3.  **Reset de Sesión:** Borre la carpeta de perfil temporal definida en el `Iniciador Web.ps1` para limpiar cookies corruptas.

---

**© 2026 Nozhgess Engineering**
*"La estabilidad es el resultado de un diagnóstico preciso."*

