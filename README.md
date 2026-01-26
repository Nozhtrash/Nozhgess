# ⚕️ Nozhgess v3.0 LEGENDARY
> **Automatización Inteligente y Resiliente para Datos Médicos (SIGGES)**

## 🌟 La Visión de Nozhgess
Nozhgess no es solo un script; es una **plataforma de automatización de grado industrial** diseñada para eliminar la carga administrativa en el procesamiento de datos del sistema SIGGES. Construido bajo los pilares de la **transparencia, resiliencia y eficiencia**, Nozhgess permite a los profesionales de la salud enfocarse en lo que realmente importa: los pacientes.

---

## 🛠️ ¿Qué hace Nozhgess? (Transparencia Total)
La aplicación actúa como un **operador virtual** que interactúa con la plataforma SIGGES de forma segura y controlada. Sus funciones principales incluyen:

*   **Procesamiento Masivo**: Automatiza la gestión de nóminas de pacientes, reduciendo horas de trabajo manual a minutos.
*   **Validación de Datos**: Realiza verificaciones en tiempo real de RUTs, fechas y coherencia de registros clínicos.
*   **Filtrado Inteligente**: Aplica reglas de negocio personalizables (IPD, OA, APS, SIC) para priorizar casos y evitar errores humanos.
*   **NASA Luxury Resilience**: Sistema de "Circuit Breaker" y esperas inteligentes para una estabilidad extrema en plataformas médicas.
*   **Zero-Byte Clean**: Arquitectura de vanguardia optimizada para la resiliencia y libre de errores de codificación.

---

## 🚀 Inicio Rápido

### 💻 Para Usuarios (Modo Aplicación)
Si solo deseas usar la herramienta, no necesitas tocar una sola línea de código:
1.  **Instala**: Ejecuta `INSTALAR.bat` para tener el ícono en tu escritorio.
2.  **Inicia**: Usa `INICIAR_NOZHGESS.bat` para abrir la interfaz gráfica premium.
3.  **Aprende**: Lee la [Guía de Instalación Express](file:///Documentacion/Instalacion.md).

### ⌨️ Para Desarrolladores (Modo IDE)
Si deseas extender Nozhgess o usarlo desde tu entorno de desarrollo:
1.  **Dependencias**: `pip install -r App/requirements.txt`.
2.  **Entrada**: El punto de acceso es [`App/Nozhgess.pyw`](file:///App/Nozhgess.pyw).
3.  **Configuración**: Todas las misiones y logs se gestionan desde la raíz para tu comodidad.

---

## 📂 Anatomía del Proyecto
Hemos organizado Nozhgess para que sea limpio y fácil de navegar:

| Carpeta | Propósito |
| :--- | :--- |
| **[`App/`](file:///App)** | El "Cerebro". Código fuente, lógica de automatización y UI. |
| **[`Documentacion/`](file:///Documentacion)** | El "Manual". Guías detalladas, transparencia y aspectos legales. |
| **[`Lista de Misiones/`](file:///Lista%20de%20Misiones)** | Tu biblioteca de tareas configuradas. |
| **[`Mision Actual/`](file:///Mision%20Actual)** | Donde ocurre la magia en este momento. |
| **[`Logs/`](file:///Logs)** | Registro histórico de cada acción realizada. |

---

## 🔒 Seguridad y Privacidad
*   **Sin Almacenamiento Remoto**: Nozhgess procesa los datos localmente en tu computadora. Nada se sube a la nube.
*   **Transparencia de Código**: Todo el motor es visible en la carpeta `App/src`, permitiendo auditorías de seguridad completas.

---

### 🎨 Créditos y Copyright
Desarrollado con ♥ por **Nozhtrash**.  
© 2026. Todos los derechos reservados. Licencia MIT.
