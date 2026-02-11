# 📘 GUÍA OPERATIVA MAESTRA: NOZHGESS v3.5.1
> **Para:** Auditores Clínicos y Supervisores GES
> **Objetivo:** Ejecución impecable de auditorías forenses automatizadas.

---

## 1. Conceptos Clave (Lo Nuevo en v3.5.1)

### A. Reportes Dinámicos
Olvídese de las columnas vacías. Nozhgess ahora genera **solo las columnas necesarias** para su misión.
- Si su misión busca 3 objetivos, el Excel tendrá `Obj [Cod 1]`, `Obj [Cod 2]` y `Obj [Cod 3]`.
- Si no busca habilitantes, no verá columnas de habilitantes.

### B. Precisión Forense
- **Fallecido:** Ahora verá la **FECHA EXACTA** de defunción (ej. `15-08-2025`), no un simple "Sí". Esto le permite cruzar datos con la fecha de garantía.
- **Observaciones Limpias:** La columna "Observación" estará vacía por defecto. Si ve algo escrito ahí, **PRESTE ATENCIÓN**: significa que hubo un error técnico grave (ej. "Sin Mini-Tabla") o una nota manual suya.

### C. Habilitante Vigente (El Semáforo)
La columna `Hab Vi` es su mejor amiga. Le dice si el paciente cumple los requisitos de entrada (diagnósticos previos) en la fecha de la nómina, independientemente de qué columnas visualice.

---

## 2. Flujo de Trabajo Diario

### Paso 1: Preparación (El "Gancho")
1.  Abra **Microsoft Edge** e inicie sesión en SIGGES con sus credenciales.
2.  Navegue a cualquier página interna de SIGGES (ej. Bandeja de Entrada) y **mantenga la pestaña abierta**.
3.  Ejecute el acceso directo **"ACCESO_NOZHGESS"** en su escritorio.
    *   *Nota: Nozhgess "parasitará" su sesión de Edge. No necesita loguearse de nuevo.*

### Paso 2: Configuración de la Misión
1.  En el Panel de Control, seleccione su Misión (ej. "Diabetes_v2").
2.  Verifique los parámetros clave:
    *   **Días Vigencia:** Ventana de tiempo para buscar antecedentes (ej. 365 días).
    *   **Max Años:** Antigüedad máxima de la historia clínica a revisar.
3.  Cargue su archivo Excel de pacientes (debe tener RUT y Fecha).

### Paso 3: Ejecución y Monitoreo
1.  Presione **"INICIAR AUDITORÍA"**.
2.  Observe la consola (terminal negra):
    *   **Texto Verde:** Paciente procesado correctamente.
    *   **Texto Amarillo/Naranja:** Alertas de coincidencias o advertencias.
    *   **Texto Rojo:** Errores críticos (Internet caído, SIGGES lento).
3.  **IMPORTANTE:** No cierre la ventana de Edge mientras el robot trabaja. Puede minimizarla, pero no cerrarla.

### Paso 4: Análisis del Reporte (Excel)
El sistema generará un archivo `Analisis_Misiones_...xlsx` en la carpeta `Resultados`.

#### Estructura del Excel:
1.  **Hoja "Detalle":** Cada fila es un paciente.
    - **Azul:** Datos del paciente (RUT, Edad, Fecha Fallecimiento).
    - **Verde:** Habilitantes encontrados y Vigencia (`Hab Vi`).
    - **Rojo:** Excluyentes (Patologías que descartan el caso).
    - **Analítica:** Columnas dinámicas `Obj` con fechas de cumplimiento.
2.  **Hoja "Diccionario":** Explicación técnica de qué significa cada columna en *su* reporte específico.
3.  **Hoja "Carga Masiva":** (Opcional) Estructura lista para subir a plataformas de gestión.

---

## 3. Solución de Problemas Comunes

### 🔴 "El sistema dice 'Error Fatal de Conexión'"
- **Causa:** Edge se cerró o SIGGES cerró la sesión por inactividad.
- **Solución:** Cierre la terminal negra, vuelva a loguearse en Edge y ejecute Nozhgess de nuevo.

### 🟡 "La columna Observación dice 'Sin Mini-Tabla'"
- **Significado:** El robot buscó el RUT pero SIGGES no mostró la tabla de casos.
- **Acción:** Verifique ese RUT manualmente. Puede ser un error de digitación en su Excel de entrada o un fallo puntual de SIGGES.

### 🟠 "No aparecen mis objetivos en el Excel"
- **Causa:** Probablemente la misión no tiene códigos configurados o ninguno de los pacientes tenía esos códigos.
- **Verificación:** Revise la configuración de la misión en el Panel de Control.

---
**© 2026 Nozhgess Operations**
