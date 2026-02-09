# 🗺️ MAPA DE DATOS Y SCRAPING: CARTOGRAFÍA v3.5.1
> **Audiencia:** Mantenedores de Selectores, Desarrolladores Backend y Auditores de Datos.
> **Propósito:** Mapeo microscópico entre la estructura HTML de SIGGES, la lógica de extracción en Python y el reporte final Integrado.

---

# 1. EL MOTOR DE NAVEGACIÓN Y BÚSQUEDA

### 1.1. Inyección de Datos Segura
El sistema utiliza `integrator.py` para normalizar los RUTs (con/sin puntos, con/sin guión) antes de enviarlos al `SiggesDriver`.
1.  **Limpieza:** `driver.clear_input(selector)`.
2.  **Inyección:** Escribe el RUT con guión y DV.
3.  **Disparo:** Presiona la lupa y espera hasta 20 segundos (`ESPERA_BUSQUEDA`).

---

# 2. ESCANEO DE LA MINI-TABLA (GATEKEEPER)

### 2.1. Algoritmo de Selección Inteligente
Ubicado en `Conexiones.py`, el método `seleccionar_caso_inteligente` ahora evalúa:
- **Estado:** Prioriza "Vigente" sobre "Cerrado".
- **Similarity:** Calcula la distancia de Levenshtein entre el nombre del problema de salud en SIGGES y los términos en el JSON.
- **Caso en Contra:** Si se detecta un caso que no coincide con la misión pero pertenece al mismo paciente, se extrae el ID de fila para una auditoría secundaria automática.

---

# 3. EXTRACCIÓN DE SUB-TABLAS (DEEP SCRAPING)

El motor opera sobre 4 dimensiones de datos mediante `DataParsingMixin`:

### 3.1. IPD (Informes Diagnósticos) - `ipd-table`
- `td[3]` -> **Fecha de Emisión**.
- `td[8]` -> **Estado Confirmación**. Si dice "SÍ", se marca el hito diagnóstico.

### 3.2. OA (Órdenes de Atención) - `oa-table`
- `td[10]` -> **Código Prestación**. Comparado contra la lista blanca del JSON para alertas de Habilitantes.
- `td[14]` -> **Estado Orden**. Descarta automáticamente órdenes "Anuladas".

---

# 4. PROTOCOLO "CSS DRIFT" (REPARACIÓN PASO A PASO)

Si el reporte dice "Sin Información" pero el dato está en SIGGES:
1.  **Captura del DOM:** `F12` -> Elements.
2.  **Identificación:** Buscar el nodo `td` que contiene la información.
3.  **Actualización:** Modificar `locators.py` y resetear el `driver` para que tome los nuevos selectores sin reiniciar la app.

---

# 5. GENERACIÓN DEL EXCEL (DATA PAINTING V3)

- **Sanitización:** `Formatos.py` limpia caracteres invisibles (UTF-8 BOM) antes de escribir en Excel.
- **Styling Dinámico:** `Excel_Revision.py` aplica el "Estilo Forense" (Encabezados Azul Profundo, Celdas con validación de color por edad y estatus).

---

**© 2026 Nozhgess Data Logistics**
*"La verdad clínica reside en la precisión del selector."*

