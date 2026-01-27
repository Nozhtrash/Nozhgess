# Funciones Avanzadas (`App/src/features/advanced_functions.py`)

## 📌 Propósito
Este módulo es la "Caja de Herramientas Premium" del sistema moderno.
A diferencia del `core` legacy que era monolítico, este módulo ofrece componentes reutilizables y desacoplados para tareas complejas como monitoreo, reintentos inteligentes y generación de reportes ejecutivos.

## 🧠 Componentes Principales

### 1. `AdvancedDataProcessor`
El procesador de datos de siguiente generación.
*   **Validación Multinivel**: No solo valida RUTs, valida la *calidad* del dato (longitud de nombres, formato de fechas).
*   **Detección de Duplicados**: Identifica grupos de duplicados y permite eliminar redundancias inteligentemente.
*   **Generador de Recomendaciones**: Analiza el dataset y sugiere mejoras (ej: "Dataset > 10000 filas, considere batch processing").

### 2. `RealTimeMonitor`
Sistema de telemetría en vivo.
*   Permite ver la velocidad de procesamiento (items/segundo) en tiempo real.
*   Mantiene un historial de métricas en memoria (rolling window de 1000 items).
*   **Uso en GUI**: La interfaz gráfica se suscribe a este monitor para mover las barras de progreso.

### 3. `SmartRetryManager`
Una evolución del viejo sistema de reintentos.
*   **Backoff Exponencial**: `Wait = 2 ^ attempt`.
*   **Circuit Breaker**: Si un servicio falla 3 veces seguidas en < 5 minutos, abre el circuito automáticamente.
*   **Operation ID**: Rastrea reintentos por "hash" de operación única.

### 4. `AutomatedReportGenerator`
El entregable para gerencia.
*   Genera un **Excel Multi-Hoja**:
    *   `Resumen Ejecutivo`: Tasas de éxito.
    *   `Métricas`: Throughput y errores.
    *   `Recomendaciones`: Texto generado por IA simbólica.

## ⚠️ Diferencias con Legacy
*   El legacy escribía directo a consola; este módulo usa colas (`queue`) y threads para no bloquear la UI.
*   El legacy usaba `openpyxl` crudo; este usa abstracciones sobre pandas.
