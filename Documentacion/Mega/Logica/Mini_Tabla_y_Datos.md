# Lógica de Extracción: Mini Tabla (`Mini_Tabla.py`)

## 📌 Propósito y Definición
La "Mini Tabla" es la tabla de resultados que aparece justo después de buscar un RUT.
Es el punto crítico de decisión: **¿Tiene casos este paciente? ¿Cuál abrimos?**
Si este módulo falla, el paciente se marca erróneamente como "Sin Caso".

## 🚀 Optimización "Tier SSS+" (JavaScript Injection)
Históricamente, leer esta tabla era lento (Selenium `find_elements` x cada celda).
La versión actual usa una técnica avanzada: **Inyección de JavaScript**.

### Mecánica (Líneas 124-160)
1.  El script envía un bloque de código JS al navegador (`driver.execute_script`).
2.  El navegador ejecuta el loop de extracción **en local** (instantáneo).
3.  Retorna un objeto JSON limpio a Python.
*   **Resultado**: Reduce el tiempo de lectura de ~650ms a ~200ms.

## 📊 Fuente de Datos (Normativa GES 2025)
La lógica de extracción y validación se basa en la **Trazadora 2025 v.3** (ver `ANALISIS_DATOS.md` en Legacy).
*   **Códigos Trazadores**: Se usan para detectar Habilitantes.
*   **Códigos de Problema**: Del 1 al 99 (ej: Diabetes T1 = Key 6).
*   **Estructura de Columnas**: Identificada en el Excel Trazadora (Col 8 = Trazadora, Col 18 = Excluyentes).

## ⚙️ Inteligencia de Auto-Detección
El script no confía ciegamente en que la columna 2 sea el estado.
Implementa `_auto_detectar_columnas`:
1.  Lee los headers (`th`) de la tabla.
2.  Busca palabras clave ("estado", "cierre", "problema").
3.  Construye un mapa dinámico (ej: `{'estado': 3, 'nombre': 1}`).
4.  Si falla la detección (tabla sin headers), usa un mapa **hardcodeado de fallback** basado en la última versión conocida de SIGGES.

## 🧹 Normalización de Datos
Antes de entregar los datos al orquestador, `Mini_Tabla.py`:
1.  **Limpia Nombres**: Elimina basura como "Decreto 140", "Dec. 44", etc. del nombre del caso.
2.  **Parsea Fechas**: Convierte strings "01/01/2026" a objetos nativos o formato estándar.

## ⚠️ Debilidades y Puntos de Falla (Honestidad Brutal)
1.  **Race Condition "Tabla Vacía"**: A veces el `tbody` aparece 500ms antes que las filas (`tr`). Si el script lee en ese instante exacto, reportará 0 casos. (Se mitiga con `WebDriverWait` explícito para `tr[td]`, pero es un riesgo latente).
2.  **Filtrado Agresivo**: El script descarta filas que no tengan "problema". Si SIGGES cambia el formato y la columna del nombre se mueve, el script podría descartar TODOS los casos pensando que son filas vacías.
3.  **Fallback Lento**: Si la inyección JS falla (por seguridad del navegador o error de sintaxis), cae al método `BeautifulSoup` o Selenium puro, que es mucho más lento y podría causar timeouts en cadena.
