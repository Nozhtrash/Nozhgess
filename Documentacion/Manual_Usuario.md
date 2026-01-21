# 📖 Manual del Usuario (Operación)

Esta guía te ayudará a dominar el uso diario de Nozhgess a través de su interfaz gráfica premium.

---

## 🖥️ La Interfaz Principal

Al iniciar Nozhgess, verás cuatro secciones principales:

### 1. Panel de Control (Izquierda)
*   **Estado del Robot**: Indica si el motor está listo, ejecutando o en pausa.
*   **Botón INICIAR**: El motor comenzará a procesar la misión cargada.
*   **Botón DETENER**: Detiene la ejecución de forma segura al finalizar el ciclo actual.

### 2. Visor de Misión (Centro)
*   Muestra los detalles del paciente que se está procesando actualmente.
*   Visualiza el progreso total (ej: `Paciente 5 de 150`).

### 3. Configuración en Tiempo Real (Derecha)
*   **Modo Potato**: Optimiza la interfaz para computadoras con pocos recursos.
*   **Nivel de Log**: Controla cuánto detalle quieres ver en la consola.
*   **Temas**: Personaliza tu experiencia con más de 20 colores de acento.

---

## 📋 Pasos para una Revisión Exitosa

### Paso 1: Cargar la Misión
Ve a la pestaña de **Misiones** y selecciona la tarea que deseas realizar. Nozhgess cargará automáticamente los archivos Excel necesarios del directorio `Lista de Misiones/`.

### Paso 2: Preparar el Navegador
Asegúrate de haber iniciado el navegador Edge usando el script `Iniciador Web.ps1` dentro de la carpeta `Iniciador/`.

### Paso 3: Iniciar la Revisión
Haz clic en el botón verde **▶️ INICIAR REVISIÓN**. Observarás cómo Nozhgess toma el control de la ventana de Edge.

---

## ⚠️ Cómo Resolver Errores

Si durante la ejecución aparece un mensaje de error:
1.  **Revisa el Log**: En la parte inferior de la app verás un registro de lo que pasó.
2.  **Verifica la Conexión**: Asegúrate de que la página de SIGGES no se haya caído. Nozhgess intentará reconectar automáticamente mediante su sistema de "Circuit Breaker".
3.  **Logs de Crash**: Si la app se cierra inesperadamente, busca el reporte detallado en la carpeta `Crash_Reports/` de la raíz.

---
© 2026 Nozhgess Team.
