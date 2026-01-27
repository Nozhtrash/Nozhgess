# Sistema de Configuración Global (`Mision_Actual.py`)

## 📌 Propósito y Definición
Este archivo es la **Única Fuente de Verdad** para la ejecución del script.
Aunque el Panel de Control (GUI) parece ser quien manda, en realidad lo único que hace la GUI es **sobrescribir este archivo**.
El script de Python NO lee la GUI; lee `Mision_Actual.py`.

## ⚙️ Estructura de Datos

### 1. Identificación (`NOMBRE_DE_LA_MISION`)
Define el contexto visual de los logs.

### 2. Rutas (`RUTA_ARCHIVO_ENTRADA`, `RUTA_CARPETA_SALIDA`)
*   **Crítico**: Rutas absolutas al Excel de pacientes y dónde guardar el resultado.
*   **Nota**: Deben usar doble backslash `\\` o slash simple `/` para evitar errores de escape en Windows.

### 3. Parámetros de Negocio
*   `VENTANA_VIGENCIA_DIAS` (Default: 100): Cuántos días atrás mirar para considerar una prestación como "vigente".
*   `MAX_REINTENTOS_POR_PACIENTE` (Default: 5): Cuántas veces intentar buscar un RUT antes de rendirse.

### 4. Switches de Motor (`REVISAR_...`)
Boleans (`True`/`False`) que apagan o encienden secciones enteras del motor de análisis.
*   `REVISAR_IPD`: Si `False`, el script NI SIQUIERA abre la pestaña de IPD (ahorra tiempo).
*   `REVISAR_OA`: Controla lectura de Órdenes de Atención.
*   etc.

### 5. `MISSIONS` (La Lista Maestra)
Es una lista de diccionarios, aunque actualmente soporta solo 1 misión activa.
Contiene la lógica de filtrado específica:
*   `keywords`: Qué palabras buscar en el nombre del caso (ej: "Depresión").
*   `habilitantes`: Lista de códigos (ej: "0801001") a buscar.
*   `familia`, `especialidad`: Metadatos para el Excel final.

## ⚠️ Debilidades y Puntos de Falla (Honestidad Brutal)
1.  **Sobrescritura Destructiva**: Cada vez que das click en "Usar Ahora" en la GUI, este archivo es aniquilado y reescrito desde cero. No guardes comentarios ni lógica custom aquí; desaparecerán.
2.  **Inyección de Código**: Como es un archivo `.py` que se importa, si la GUI escribiera código malicioso o con errores de sintaxis aquí, el script principal crashearía al inicio (`SyntaxError`).
3.  **Hardcoding Temporal**: A veces variables como `INDICE_COLUMNA_RUT` están hardcodeadas a 0. Si el Excel de entrada cambia de formato, hay que editar esto manualmente o desde una GUI que lo soporte.

## 🔄 Flujo de Vida
1.  Usuario selecciona Misión en GUI -> Click "Usar Ahora".
2.  GUI genera string de Python y sobrescribe `Mision_Actual.py`.
3.  Usuario inicia `Iniciador Script.py`.
4.  Scrip importa `Mision_Actual`.
