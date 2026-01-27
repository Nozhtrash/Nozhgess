# Optimización de Rendimiento (`App/src/utils/performance_optimizer.py`)

## 📌 Propósito
Módulo crítico para manejar datasets grandes (>50MB) sin colapsar la memoria RAM.
Implementa estrategias de "Lazy Loading" y "Type Downcasting".

## ⚙️ Mecanismos de Optimización

### 1. `optimize_dataframe_memory(df)`
La función estrella. Reduce el peso de un DataFrame hasta en un 70%.
*   **Downcasting Numérico**: Convierte `int64` a `int8`, `int16` o `uint8` según el valor máximo de la columna.
*   **Categorización**: Convierte columnas de texto (`object`) repetitivas a `category`.
    *   *Regla*: Si `unique_values / total_values < 0.5`.

### 2. `process_excel_in_chunks`
Lectura por lotes.
*   Si el archivo pesa > 50MB, no lo carga entero en RAM.
*   Usa generadores de Python (`yield`) para leer 1000 filas a la vez.

### 3. `performance_monitor` (Context Manager)
Herramienta de profiling en producción.
```python
with optimizer.performance_monitor("Validacion_Batch_1"):
    procesar_datos()
# Log: [PERF] Validacion_Batch_1: 0.1s, Memory: +2.5MB
```

### 4. Decorador `cache_validation_results`
Evita validar el mismo RUT 500 veces.
*   Implementa un caché LRU (Least Recently Used) simple de 1000 items.
*   Acelera drásticamente datasets con muchos duplicados.

## 🛡️ Compatibilidad
Este módulo inyecta "Parches" en el código legacy (`enhance_existing_validations`) para que el sistema antiguo se vuelva rápido sin reescribirlo.
