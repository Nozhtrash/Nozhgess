# 🖥️ DEEP DIVE FRONTEND: ARQUITECTURA GUI v3.5.1
> **Audiencia:** Diseñadores UI, Desarrolladores Python y Mantenedores de Interfaz.
> **Propósito:** Guía microscópica sobre el funcionamiento, diseño y optimización de la interfaz de Nozhgess.

---

## 1. ARQUITECTURA "SPA" (SINGLE PAGE APPLICATION) EN TKINTER

Aunque Nozhgess es una aplicación de escritorio, su arquitectura interna imita a una SPA moderna.

### 1.1 El Shell de la Aplicación (`app.py`)
Es el contenedor raíz. Su única función es orquestar el cambio de vistas.
- **`self.container`:** Un `CTkFrame` que ocupa el 100% de la ventana.
- **`self.show_frame(name)`:** El método nuclear. Utiliza `.grid_forget()` para ocultar la vista actual y `.grid()` para mostrar la nueva. Esto evita fugas de memoria por creación constante de widgets.

### 1.2 Vistas Especializadas v3.5.1
- **`RunnerView`:** Ahora integra el `RealtimeMonitor`. Muestra barras de progreso dinámicas y contadores de validación.
- **`ConfigView`:** Editor JSON con resaltado de sintaxis y autocompletado de campos de misión.

---

## 2. EL PUENTE DE HILOS (THREADING BRIDGE)

Tkinter **NO** es thread-safe. Si el robot intenta cambiar un texto directamente, la app colapsará.

### 2.1 El Patrón Productor-Consumidor (IPC)
- **El Productor (Worker):** El hilo del robot (`integrator.py`) envía diccionarios de estado a la `log_queue`.
- **El Monitor en Tiempo Real:** Intercepta métricas de rendimiento y las envía al hilo principal mediante callbacks seguros.
- **El Consumidor (Main Thread):** La función `self.after(50, self._drain_queue)` actualiza la pantalla con una frecuencia de 20fps.

---

## 3. OPTIMIZACIÓN DE LA CONSOLA Y MÉTRICAS

### 3.1 Gestión de Memoria de Consola
Para evitar que la UI se ralentice tras 5 horas de ejecución:
- **Buffer Circular:** La consola mantiene exactamente 3.000 líneas. Al entrar la 3.001, la primera se borra físicamente del widget.
- **Async Highlighting:** El resaltado de búsqueda se realiza en bloques para no congelar la entrada del usuario.

### 3.2 Visualización de Métricas (New)
- **Validation Widgets:** Indicadores visuales (Círculos Verde/Rojo) que muestran el estado de los últimos 10 RUTs procesados sin necesidad de leer el log.

---

## 4. SOLUCIÓN DE PROBLEMAS GRÁFICOS (DETALLADO)

| Síntoma | Causa Técnica | Solución Forense |
| :--- | :--- | :--- |
| **"La ventana se queda en 'Cargando...'"** | El `integrator` no detectó el sistema legacy. | Verificar logs de consola. Reiniciar desde `Nozhgess.pyw`. |
| **"Los contadores no se mueven"** | El `callback` de métricas se desconectó del hilo principal. | Presionar "Reset" en la UI para reinicializar el puente IPC. |
| **"Flickering en la tabla"** | Frecuencia de actualización `self.after` demasiado alta. | El sistema autodetecta lag y baja a 100ms si el CPU supera el 80%. |

---

## 5. PERSONALIZACIÓN DE TEMAS (`ThemeSystem`)
Nozhgess v3.5.1 utiliza un motor de temas asíncrono que permite cambiar de **Modo Oscuro** a **Modo Claro** sin detener la misión, recalculando los colores de los tags de la consola en tiempo real.

---
**© 2026 Nozhgess UI LABS**
