# 📕 DICCIONARIO MAESTRO DE ERRORES Y SOLUCIONES
> **Versión:** 1.0 (Feb 2026)
> **Nivel de Detalle:** Forense / Infraestructura

Este documento es la referencia definitiva para diagnosticar y reparar Nozhgess. Los errores se clasifican por su origen y severidad.

---

# 1. ERRORES DE INFRAESTRUCTURA (NIVEL ROJO)
*Estos errores impiden que el robot siquiera comience su trabajo.*

| Código / Mensaje | Causa Raíz | Solución Técnica |
| :--- | :--- | :--- |
| **`ConnectionRefusedError`** | El puerto 9222 de Edge no está abierto o el script PS1 no se ejecutó. | Cierre Edge, ejecute `Iniciador Web.ps1` y verifique que la ventana de Edge cargue. |
| **`WebDriverException: DevToolsActivePort file doesn't exist`** | El perfil de Edge especificado en el PS1 está bloqueado por otra instancia. | Mate el proceso `msedge.exe` desde el Administrador de Tareas y reintente. |
| **`SessionNotCreatedException`** | La versión de Edge se actualizó y el Driver quedó obsoleto. | Descargue el `msedgedriver.exe` correspondiente a su versión de Edge y reemplácelo en `App/bin`. |

---

# 2. ERRORES DEL MOTOR DE ANÁLISIS (NIVEL NARANJA)
*El robot corre, pero falla al procesar ciertos pacientes.*

### 2.1. `TimeoutException` en Búsqueda
- **Síntoma:** El robot escribe el RUT pero nunca hace click en la lupa o se queda esperando la tabla.
- **Solución Forense:** 
    1. Revise la velocidad del internet del hospital.
    2. Aumente el valor de `ESPERA_BUSQUEDA` en `App/src/utils/Esperas.py`.
    3. Verifique si SIGGES lanzó un popup de "Aviso del Sistema" que bloquea la vista.

### 2.2. `StaleElementReferenceException`
- **Síntoma:** El robot intenta leer una fecha y lanza un error de "referencia vieja".
- **Solución Forense:** 
    - El sistema ya reintenta automáticamente, pero si persiste, asegúrese de que el método `_invalidar_cache_estado()` se llame antes de entrar a la cartola del paciente.

---

# 3. ERRORES DE LÓGICA CLÍNICA (NIVEL AMARILLO)
*El robot termina, pero los datos en el Excel no guardan sentido.*

### 3.1. "Caso en Contra detectado pero columnas vacías"
- **Causa:** Las `keywords_contra` en el JSON son demasiado específicas.
- **Solución:** Use términos más cortos. En lugar de "Diabetes Mellitus Tipo 1 Descompensada", use solo "Tipo 1".

### 3.2. "Fechas Habilitantes no aparecen en rojo"
- **Causa:** El código de prestación en SIGGES tiene espacios al final o el JSON tiene el código mal escrito.
- **Solución:** Revise `latest.log`. El robot imprime: `[DEBUG] Comparando Código Web: '5002101 ' con JSON: '5002101'`. Si hay espacios, el motor de normalización (`Formatos.py`) debe ser actualizado.

---

# 4. PROTOCOLO DE REPORTE DE ERRORES (SOPORTE)

Si el error no está en este diccionario:
1.  **NO REINTENTE** más de 3 veces si el fallo es idéntico.
2.  **CAPTURE:** El contenido de la carpeta `Logs/` y una captura de pantalla de la consola de Nozhgess.
3.  **REVISE:** Si SIGGES está en "Mantención" (Suele ocurrir los fines de semana o después de las 20:00 hrs).

---

**© 2026 Nozhgess Support & Engineering**
*"La estabilidad es el resultado de un diagnóstico preciso."*
