# 🩺 NOZHGESS: Clinical Grade Automation Platform v3.2

[![Version](https://img.shields.io/badge/Version-3.2.0_Nuclear-blue?style=for-the-badge)](./Documentacion/CHANGELOG.md)
[![Architecture](https://img.shields.io/badge/Architecture-MVC--S-orange?style=for-the-badge)](./Documentacion/BIBLIA_TECNICA_NOZHGESS.md)
[![Engine](https://img.shields.io/badge/Engine-Selenium_Hybrid-43B02A?style=for-the-badge&logo=selenium&logoColor=white)]()
[![UI](https://img.shields.io/badge/UI-CustomTkinter_Pro-7c4dff?style=for-the-badge)](./Documentacion/DOCUMENTACION_FRONTEND_PROFUNDA.md)
[![Status](https://img.shields.io/badge/Status-Producción_Estable-success?style=for-the-badge)]()

> **"Robustez sobre Velocidad. Verdad sobre Suposición."**
>
> **Nozhgess** no es simplemente un script de automatización ("bot"); es una **Plataforma de Auditoría Clínica Cibernética**. Diseñada para operar en entornos hospitalarios críticos donde la precisión de los datos es vital. Su arquitectura híbrida (Python + PowerShell + JS Injection) le permite navegar la plataforma gubernamental SIGGES con una estabilidad que supera a cualquier operador humano.

---

## 🌌 Visión General y Capacidades

Nozhgess fue construido para resolver el problema del "Fatiga del Auditor": revisar cientos de casos GES, navegar múltiples pestañas, calcular fechas y detectar códigos específicos en historiales clínicos masivos, todo sin cometer un solo error.

### 🔥 Superpoderes Técnicos
1.  **Inyección de Sesión (Session Parasitism):**
    *   A diferencia de los bots convencionales que abren un navegador "limpio" (y bloqueado por seguridad), Nozhgess se **conecta** a una instancia de Microsoft Edge ya abierta por el usuario.
    *   **Beneficio:** Hereda automáticamente la autenticación, Cookies y Certificados de Seguridad.
    *   **Tecnología:** Protocolo Chrome DevTools (CDP) sobre puerto `localhost:9222`.

2.  **Navegación "Nuclear" (Atomic Actions):**
    *   El motor no confía en el navegador. Si un botón está tapado por un "overlay" transparente o un anuncio, Nozhgess no falla.
    *   **Estrategia de 3 Capas:**
        1.  Intento de Click Nativo (Simulación de Mouse).
        2.  **Fallback de Inyección JS:** `arguments[0].click()` (Bypass de UI).
        3.  **Disparo de Eventos:** Fabrica eventos `mousedown`/`mouseup` sintéticos para engañar a frameworks React/Angular modernos.

3.  **Visión Computacional de Estado (Smart Wait):**
    *   No usa tiempos fijos (`sleep(5)`). El robot "ve" el spinner de carga (`dialog.loading`).
    *   **Algoritmo:** Mantiene el freno presionado exactamente los milisegundos que el spinner está visible. Si la red es lenta, espera. Si es rápida, vuela.

4.  **Generación de Evidencia Forense:**
    *   El resultado no es texto plano. Es un archivo Excel (`.xlsx`) con semántica de colores.
    *   **Rojo:** Alerta Médica (Habilitante encontrado).
    *   **Verde:** Cumplimiento Normativo.
    *   **Azul:** Datos Demográficos.

---

## 🧠 Inteligencia y Tiempos de Reacción

El núcleo del sistema está calibrado para la estabilidad ("Reliability First").

### La Regla del "1.0s Safety Brake"
En `src/core/modules/core.py`, existe una línea inamovible: `time.sleep(1.0)`.
*   **¿Por qué?** SIGGES es una aplicación web SPA (Single Page Application). A veces, el navegador dice "Listo" pero el Javascript interno aún está renderizando la tabla.
*   **Efecto:** Este segundo de silencio táctico elimina el 99% de los "Falsos Negativos" (decir que un dato no está cuando sí estaba).

### El Cerebro de Datos (`mission_config.json`)
Nozhgess no está "harcodeado". Es configurable.
*   Puede auditar **Diabetes Tipo 1** hoy y **Hipertensión** mañana, simplemente cargando una "Misión" (JSON) diferente.
*   Define dinámicamente qué códigos de prestaciones (`5002101`, `0801101`) son relevantes para cada patología.

---

## 🏗️ Anatomía del Proyecto (Estructura Profunda)

El proyecto sigue una arquitectura **MVC-S (Model-View-Controller-Service)** estricta para garantizar mantenibilidad a largo plazo.

### 📂 Mapa de Carpetas

```text
Nozhgess/
├── 🚀 Nozhgess.pyw            # [ENTRY POINT] Gatillo silencioso. Configura PYTHONPATH.
├── 📂 App/
│   ├── 📂 config/             # [CEREBRO]
│   │   └── mission_config.json # Reglas de negocio (Códigos, Plazos, Columnas).
│   ├── 📂 src/
│   │   ├── 📂 core/           # [MOTOR]
│   │   │   ├── Driver.py      # Wrapper Selenium Edge. Maneja la conexión 9222.
│   │   │   ├── locators.py    # [BIBLIA] Diccionario de XPaths. Si SIGGES cambia, esto se edita.
│   │   │   └── modules/core.py # Lógica "Nuclear" de clicks y esperas.
│   │   ├── 📂 gui/            # [ROSTRO]
│   │   │   ├── app.py         # Ventana Principal CustomTkinter.
│   │   │   ├── theme.py       # Sistema de Diseño (#7c4dff, Segoe UI).
│   │   │   └── views/runner.py # Consola de Ejecución y Multithreading.
│   │   └── 📂 utils/          # [HERRAMIENTAS]
│   │       └── Excel_Revision.py # Pintor de Excel. Lógica de colores.
├── 📂 Documentacion/          # [CONOCIMIENTO] 5 Manuales Especializados.
├── 📂 Iniciador/
│   └── Iniciador Web.ps1      # [LAUNCHER] Script PowerShell vital para abrir el puerto de debug.
└── 📂 Logs/                   # [CAJA NEGRA] Registro forense de cada acción.
```

---

## 🎨 La Experiencia de Usuario (App & GUI)

La interfaz no es una ocurrencia tardía. Es una aplicación de escritorio moderna y robusta.

*   **Tecnología:** CustomTkinter (Python).
*   **Tema Premium:** Modo Oscuro nativo con acentos en **Deep Purple** (`#7c4dff`) para reducir fatiga visual del operador.
*   **Concurrencia Real:**
    *   La interfaz **NUNCA** se congela.
    *   Usa un modelo de **Worker Thread** separado para la lógica pesada.
    *   Se comunica con la UI mediante una **Cola de Mensajes (`queue.Queue`)** thread-safe.
    *   Esto permite ver los logs en tiempo real mientras el robot trabaja en segundo plano.

---

## 📚 Ecosistema de Documentación

Hemos creado una biblioteca completa para cubrir cada aspecto del software. No hay cajas negras.

### 1. [📘 GUÍA OPERATIVA MAESTRA](./Documentacion/GUIA_OPERATIVA_MAESTRA.md)
*   *Para quién:* El Usuario Final.
*   *Contenido:* Manual de vuelo, semáforo de errores, interpretación de colores del Excel.

### 2. [📙 BIBLIA TÉCNICA](./Documentacion/BIBLIA_TECNICA_NOZHGESS.md)
*   *Para quién:* El Ingeniero Líder.
*   *Contenido:* Arquitectura, filosofía, dependencias y estructura lógica.

### 3. [🛠️ DEEP DIVE BACKEND (Reparación)](./Documentacion/DOCUMENTACION_BACKEND_DEEP_DIVE.md)
*   *Para quién:* Soporte Técnico / Dev.
*   *Contenido:* Cómo funciona el hook al puerto 9222, lógica de reintentos y errores fatales.

### 4. [🖥️ DEEP DIVE FRONTEND (GUI)](./Documentacion/DOCUMENTACION_FRONTEND_PROFUNDA.md)
*   *Para quién:* Diseñador UI / Dev.
*   *Contenido:* Códigos de color, arquitectura de vistas y sistema de logs visuales.

### 5. [🗺️ MAPA DE DATOS (Selectores)](./Documentacion/DOCUMENTACION_MAPA_DE_DATOS.md)
*   *Para quién:* Mantenedor de Selectores.
*   *Contenido:* La relación 1:1 entre cada columna del Excel, cada variable de Python y cada elemento HTML (`td[3]`) de la web.

---

## ⚙️ Guía de Instalación y Requisitos

### Prerrequisitos de Hardware/Software
*   **OS:** Windows 10 o 11 (x64).
*   **Navegador:** Microsoft Edge (Chromium).
*   **Office:** Microsoft Excel (Para abrir los reportes).
*   **Conectividad:** Acceso a Internet estable.

### Configuración del Entorno
1.  **Driver:** El archivo `msedgedriver.exe` debe coincidir con su versión de Edge. (Ubicado en `App/bin` o `System32`).
2.  **Puerto:** El puerto `9222` debe estar libre (Nozhgess lo usa para controlar Edge).

### Ejecución (El Flujo de Trabajo)
1.  **Lanzamiento:** Ejecute `Nozhgess.pyw`.
2.  **Inyección:** Presione "Iniciar Edge (Debug)". Esto corre el script `.ps1` oculto.
3.  **Login:** En la ventana de Edge que se abre, inicie sesión en SIGGES manualmente.
4.  **Carga:** Arrastre su Excel de pacientes a la app.
5.  **Acción:** Presione "EJECUTAR". El robot tomará el control.

---

## 🛡️ Solución de Problemas (Troubleshooting)

| Síntoma | Diagnóstico Probable | Solución |
| :--- | :--- | :--- |
| **"Connection Refused"** | El puerto 9222 está cerrado. | Cierre todo Edge. Use el botón "Iniciar Edge" de la App. |
| **"Session Not Created"** | Driver incompatible. | Actualice `msedgedriver.exe`. |
| **"Timeout" constante** | SIGGES está muy lento. | El sistema reintentará 3 veces. Si persiste, pause 5 min. |
| **Excel sin colores** | Error en `Excel_Revision.py`. | Verifique que no se haya borrado la carpeta `themes`. |

---

## 🏆 Créditos y Licencia

**Desarrollado con pasión por la eficiencia clínica.**
Este software representa miles de horas de ingeniería de precisión para garantizar que ningún paciente GES pierda su garantía por un error administrativo.

*   **Versión:** 3.2.0 "Nuclear"
*   **Licencia:** Privada / Interna
*   **Año:** 2026

---
**Nozhgess:** *Donde la medicina se encuentra con la tecnología.*
