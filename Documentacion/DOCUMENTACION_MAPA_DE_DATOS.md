# 🗺️ MAPA DE DATOS Y SCRAPING: CARTOGRAFÍA v3.5.0
> **Audiencia:** Mantenedores de Selectores, Desarrolladores Backend y Auditores de Datos.
> **Propósito:** Mapeo microscópico entre la estructura HTML de SIGGES, la lógica de extracción en Python y el reporte final.

---

# 1. EL MOTOR DE NAVEGACIÓN Y BÚSQUEDA

El robot no solo busca; interpreta la pantalla para asegurar que el RUT es el correcto.

### 1.1. Búsqueda Inteligente (`INPUT_RUT` / `BTN_LUPA`)
1.  **Limpieza:** El robot borra cualquier texto previo en el campo.
2.  **Inyección:** Escribe el RUT con guión y DV.
3.  **Disparo:** Presiona la lupa y espera hasta 20 segundos (`ESPERA_BUSQUEDA`).
4.  **Validación:** Si aparece el mensaje "No se encontraron registros", el robot marca al paciente como "Paciente No Encontrado" y salta al siguiente.

---

# 2. ESCANEO DE LA MINI-TABLA (GATEKEEPER)

Esta tabla es el primer filtro. Aquí se decide a qué caso entrar.

### 2.1. Algoritmo de Selección (`TABLA_CASOS`)
- **Iteración:** Escanea todas las filas (`<tr>`).
- **Data Points:**
    - `td[2]` -> Nombre del Problema de Salud.
    - `td[5]` -> Estado del Caso (Busca: "Vigente").
    - `td[1]` -> Enlace de acceso.
- **Lógica de "Caso en Contra":** Si una fila coincide con las `keywords_contra` (ej. "Diabetes Tipo 1" cuando se busca "Tipo 2"), el motor marca un flag de **Divergencia Detectada** y entra para auditar.

---

# 3. EXTRACCIÓN DE SUB-TABLAS (DEEP SCRAPING)

Una vez dentro de la cartola, el motor opera sobre 4 dimensiones de datos:

### 3.1. IPD (Informes Diagnósticos)
- **Selectores:** `//table[@id='ipd-table']//tr`
- **Mapeo Forense:**
    - `td[3]` -> **Fecha de Emisión**. (Se usa para el hito del diagnóstico).
    - `td[8]` -> **Diagnóstico Confirmado (String)**. Buscamos coincidencias con la patología.

### 3.2. OA (Órdenes de Atención)
- **Selectores:** `//table[@id='oa-table']//tr`
- **Mapeo Forense:**
    - `td[3]` -> **Fecha de la Orden**.
    - `td[10]` -> **Código Prestación (FONASA)**. Es la clave primaria para las alertas Rojas (Habilitantes).
    - `td[14]` -> **Estado**. Si dice "Anulada", se ignora.

### 3.3. SIC (Interconsultas)
- **Mapeo:** Rastrea derivaciones. Si existe una SIC vigente, el sistema marca el **Apto SE** (Seguimiento Especialista).

---

# 4. PROTOCOLO "CSS DRIFT" (REPARACIÓN PASO A PASO)

Si el reporte dice "Sin Información" pero el dato está en SIGGES, la web cambió. Siga este protocolo:

1.  **Captura del DOM:** En Edge, presione `F12` y vaya a la pestaña "Elements".
2.  **Localización:** Busque el dato (ej. una fecha).
3.  **Conteo de Columnas:**
    - El primer `<td>` es `[1]`.
    - Cuente cuántos hay hasta llegar a su dato.
4.  **Actualización:** Vaya a `locators.py`. 
    - Busque la constante (ej. `OA_FECHA`).
    - Cambie el número final del XPath (ej. de `td[3]` a `td[4]`).
5.  **Verificación:** Ejecute un solo paciente para validar el cambio.

---

# 5. GENERACIÓN DEL EXCEL (DATA PAINTING)

- **Hoja Principal:** Resume la situación clínica. Colores: Rojo (Examen reciente encontrado), Verde (Proceso OK), Púrpura (Caso en Contra).
- **Hoja Carga Masiva (CYAN):** Formato estricto para subida a sistemas externos.
    - `Especialidad` y `Familia` se inyectan dinámicamente desde el `mission_config.json`.

---

**© 2026 Nozhgess Data Logistics**
*"La verdad clínica reside en la precisión del selector."*
