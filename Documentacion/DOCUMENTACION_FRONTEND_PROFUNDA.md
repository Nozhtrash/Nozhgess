# 🖥️ DEEP DIVE FRONTEND: ARQUITECTURA GUI v3.5.0
> **Audiencia:** Diseñadores UI, Desarrolladores Python y Mantenedores de Interfáz.
> **Propósito:** Guía microscópica sobre el funcionamiento, diseño y optimización de la interfaz de Nozhgess.

---

# 1. ARQUITECTURA "SPA" (SINGLE PAGE APPLICATION) EN TKINTER

Aunque Nozhgess es una aplicación de escritorio, su arquitectura interna imita a una SPA moderna.

### 1.1. El Shell de la Aplicación (`app.py`)
Es el contenedor raíz. Su única función es orquestar el cambio de vistas.
- **`self.container`:** Un `CTkFrame` que ocupa el 100% de la ventana.
- **`self.show_frame(name)`:** El método nuclear. Utiliza `.grid_forget()` para ocultar la vista actual y `.grid()` para mostrar la nueva. Esto evita fugas de memoria por creación constante de widgets.

### 1.2. Vistas Especializadas
- **`RunnerView`:** La más compleja. Gestiona el ciclo de vida del robot.
- **`ConfigView`:** Un mini-editor JSON integrado con validación de sintaxis en tiempo real.

---

# 2. EL PUENTE DE HILOS (THREADING BRIDGE)

Este es el aspecto técnico más crítico. Tkinter **NO** es thread-safe. Si el robot intenta cambiar un texto directamente, la app lanzará un `RuntimeError` o se colapsará.

### 2.1. El Patrón Productor-Consumidor
- **El Productor (Worker Thread):** El hilo del robot (`threading.Thread`) que no conoce nada de la UI. Envía mensajes a través de la `log_queue`.
- **La Cola (`queue.Queue`):** El "Tubo" de comunicación. Almacena mensajes de forma segura entre hilos.
- **El Consumidor (Main Thread):** La función `_drain_ui_queue`.
  - Se gatilla cada 100ms mediante `self.after(100, ...)` (recursividad controlada).
  - Si la cola tiene datos, los procesa y actualiza la pantalla.

---

# 3. OPTIMIZACIÓN DEL BUSCADOR DE LOGS (THE SEARCH ENGINE)

### 3.1. Gestión de Memoria y Buffering
La consola de logs (`LogConsole`) puede recibir miles de líneas. Para evitar lag:
- **Limitación de Buffer:** Si el texto supera las 5.000 líneas, el sistema borra automáticamente las primeras 500. Esto mantiene el consumo de RAM bajo control.

### 3.2. Lógica de Resaltado Dual
El buscador utiliza tags internos de Tkinter para lograr un efecto premium:
- **`match_all`:** (Background Amarillo, Texto Negro). Marca todas las coincidencias.
- **`match_current`:** (Background Naranja, Texto Blanco). Marca la posición activa.
- **Navegación:** Al presionar Enter, el sistema calcula el índice de la siguiente coincidencia y mueve el scroll `see(index)` de forma suave.

---

# 4. SOLUCIÓN DE PROBLEMAS GRÁFICOS (DETALLADO)

| Síntoma | Causa Técnica | Solución Forense |
| :--- | :--- | :--- |
| **"La ventana se queda en blanco al iniciar"** | El puerto 9222 está bloqueado o el script PS1 falló. | Verifique que Edge se abrió con el puerto 9222. Reinicie el Iniciador. |
| **"Los logs se ven cortados"** | El ancho del `RunnerView` es muy pequeño para el wrap de texto. | Expanda la ventana. El sistema soporta `word_wrap=True` dinámico. |
| **"Los botones no responden durante la ejecución"** | El hilo de la UI está bloqueado por una llamada sincrónica pesada. | Verifique que no haya llamados a `sleep()` en el hilo principal. |
| **"Error: Main loop is not running"** | Se intentó cerrar la app mientras el hilo del robot seguía vivo. | El sistema destruye el hilo al cerrar, pero si persiste, use el botón "Detener Misión". |

---

**© 2026 Nozhgess UI LABS**
*"Donde la densidad de información se vuelve elegancia operativa."*
