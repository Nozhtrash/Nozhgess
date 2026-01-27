# Interfaz Mejorada (`App/src/gui/enhanced_app.py`)

## 📌 Propósito
Reemplazo total de la antigua GUI monolítica.
Basada en `customtkinter`, ofrece modo oscuro nativo, tarjetas de estado y separación de responsabilidades.

## 🏗️ Arquitectura Visual

### 1. `ModernFrame`, `ModernButton`, etc.
Componentes abstractos que heredan de CTk pero encapsulan estilos (colores, bordes redondeados).
Esto permite cambiar el "Tema" de toda la app modificando un solo archivo (`src/gui/theme.py`).

### 2. Paneles Principales
*   **Sidebar**: Botones de acción (`Iniciar`, `Configurar`, `Logs`).
*   **Status Area**: Tarjetas estilo dashboard (`Total Procesados`, `Velocidad`).
*   **Progress Panel**: Barra de progreso real vinculada al `RealTimeMonitor`.

### 3. Loop de Simulación
Incluye un método `simulate_processing()` para demostraciones sin conectar el backend real, útil para desarrollo de UI.

## ⚠️ Integración
La App no corre la lógica de negocio en el hilo principal (UI Thread).
Lanza un `threading.Thread` que ejecuta `Conexiones.py` o `UniversalProcessor` para no congelar la ventana.
