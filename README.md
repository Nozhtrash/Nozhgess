# ⚕️ Nozhgess v3.0 LEGENDARY
> **La Suite Definitiva de Automatización para SIGGES**

![Estado](https://img.shields.io/badge/Estado-Estable-success) ![Versión](https://img.shields.io/badge/Versión-3.0.0-blue) ![Python](https://img.shields.io/badge/Python-3.10%2B-yellow)

**Nozhgess** es una obra de ingeniería diseñada para transformar la gestión de datos médicos. No es simplemente un script de automatización; es un **asistente virtual autónomo** capaz de navegar, interpretar y gestionar la plataforma SIGGES con una precisión superior a la humana y una velocidad inigualable.

---

## 📚 Documentación Exclusiva

Para mantener este manual limpio, hemos dividido la información técnica en documentos especializados. **Por favor, léelos según tu rol:**

| Icono | Documento | Descripción |
| :--- | :--- | :--- |
| 🛠️ | **[Guía de Desarrollo](DEVELOPMENT.md)** | Arquitectura, diagramas, lógica interna y filosofía de código. |
| 🚑 | **[Solución de Problemas](TROUBLESHOOTING.md)** | Guía rápida para resolver errores, bloqueos y dudas comunes. |
| 📜 | **[Historial de Cambios](CHANGELOG.md)** | Lista detallada de cada mejora, corrección y nueva funcionalidad. |
| 📥 | **[Instalación](Documentacion/Instalacion.md)** | Pasos para desplegar Nozhgess en una nueva máquina. |

---

## 🌟 Características Principales

### 🧠 Inteligencia Artificial Simulata
Nozhgess no sigue coordenadas ciegas. Utiliza **Reconocimiento Dinámico del DOM** para entender qué está pasando en la pantalla.
*   Detector de Spinners (`_wait_smart`): Sabe cuándo SIGGES está "pensando" y espera pacientemente.
*   Navegación Resiliente: Si un menú falla, intenta rutas alternativas (URL directa) automáticamente.

### 🛡️ Seguridad de Grado Militar
*   **Ejecución Local:** Tus credenciales y datos de pacientes NUNCA salen de tu red. Todo ocurre en `localhost`.
*   **Logs Forenses:** Cada acción queda registrada en auditorías inmutables en la carpeta `Logs/`.

### ⚡ Rendimiento "Zero-Latency"
*   **Hot-Reloading:** Modifica las reglas de la misión (códigos a buscar) y aplícalas sin reiniciar el programa.
*   **Parallel Logging:** Visualiza resúmenes limpios en tiempo real mientras el sistema graba trazas técnicas en segundo plano.

---

## 🚀 Cómo Empezar

### Requisitos Previos
*   Sistema Operativo: Windows 10/11.
*   Navegador: Microsoft Edge (Chromium).
*   Acceso: Credenciales activas de SIGGES.

### Ejecución
1.  **Doble clic** en `INICIAR_NOZHGESS.bat`.
2.  Se abrirá el **Dashboard de Control**.
3.  Selecciona tu Misión en el panel izquierdo o configura una nueva.
4.  Presiona **"Iniciar Edge Debug"** para abrir el navegador seguro.
5.  Loguéate en SIGGES.
6.  Presiona **"▶ Iniciar"** en Nozhgess.
7.  *Relájate y observa la magia.*

---

## ⚙️ Configuración Avanzada

Nozhgess es altamente personalizable a través de `App/config/mission_config.json`.
*   **Keywords:** Define qué palabras clave buscar en las observaciones.
*   **Códigos Habilitantes/Excluyentes:** Controla con precisión quirúrgica qué casos procesar.
*   **Tiempos de Espera:** Ajusta la velocidad según la latencia de tu red hospitalaria.

*(Ver [Guía de Desarrollo](DEVELOPMENT.md) para detalles sobre la estructura JSON)*

---

## 🤝 Contribuir y Soporte

Este proyecto es mantenido por **Nozhtrash**.
*   ¿Encontraste un bug? Revisa `TROUBLESHOOTING.md` primero.
*   ¿Tienes una idea? Abre un "Issue" en nuestro repositorio privado.

---

Copyright © 2026 Nozhtrash.  
*Diseñado para la excelencia. Construido para durar.*
