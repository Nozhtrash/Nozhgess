# Changelog

A continuación se detallan todos los cambios notables en el proyecto **Nozhgess**.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), 
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.1] - 2026-02-11
### Añadido
- **Motor de Columnas Dinámicas:** Implementación completa en `Conexiones.py`. Ahora las columnas de reporte (Objetivos, Habilitantes, Excluyentes) se generan dinámicamente según la configuración de cada misión (`Obj [Code]`, `Hab [Code]`, `Excl [Code]`), eliminando columnas estáticas vacías.
- **Formato de Fecha Unificado:** Todas las fechas en columnas dinámicas y de reporte ahora usan estrictamente el formato `dd-mm-yyyy`.
- **Detalle de Fallecimiento:** La columna "Fallecido" ahora muestra la fecha exacta de defunción en lugar de un binario "Sí/No", proporcionando contexto forense inmediato.

### Cambiado
- **Limpieza de Observaciones:** La columna "Observación" ha sido purgada de mensajes automáticos del sistema. Ahora está reservada exclusivamente para notas manuales del auditor o errores críticos de infraestructura (ej. "Sin Mini-Tabla").
- **Optimización de Frecuencias:** El validador de frecuencias (`FrequencyValidator`) fue desacoplado de la presentación visual, operando directamente sobre los datos crudos (`prestaciones`), lo que garantiza robustez independientemente del formato de salida.
- **Diccionario de Datos:** Actualización masiva de `Excel_Revision.py` para reflejar las nuevas definiciones de columnas y eliminar estilos obsoletos.

### Eliminado
- **Columna "¿Cerrado?":** Eliminada del reporte `Analisis_Misiones.xlsx` y del diccionario de estilos, ya que no aportaba valor operativo y generaba ruido visual.
- **Scripts de Depuración:** Eliminación de `debug_frecuencia.py`, `audit_limits.py` y otros scripts temporales para mantener la higiene del repositorio.

## [3.5.0] - 2026-02-04
### Añadido
- **Integración de Folio VIH:** Nueva funcionalidad para buscar códigos específicos en la tabla OA, capturar sus folios y verificar su uso en la tabla APS.
- **Configuración Granular:** Flags `require_oa` y `max_oa` activados por misión para control fino del scraping.
- **GUI de Configuración:** Nuevos controles en la interfaz para gestionar la búsqueda de Folios VIH.

### Cambiado
- **Refactorización de `Conexiones.py`:** Optimización del flujo de scraping para soportar la lógica condicional de Folio VIH sin impactar el rendimiento general.

## [3.4.2] - 2026-01-31
### Añadido
- **Auditoría Profunda:** Implementación de logs de auditoría detallados para trazabilidad completa de la ejecución.

## [3.4.0] - 2026-01-20
### Añadido
- **Validación de Frecuencias Temporales:** Motor inicial para validar periodicidad de prestaciones (V1).

## [3.3.0] - 2025-12-15
### Añadido
- **Soporte Multihilo:** Implementación de `queue.Queue` para desacoplar la interfaz de usuario del motor de scraping.

---
**© 2026 Nozhgess Foundation**
