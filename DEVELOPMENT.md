# 🛠️ Guía de Desarrollo de Nozhgess (Developer's Bible)

> **Versión del Documento:** 1.0  
> **Última Actualización:** Enero 2026

Bienvenido al núcleo de ingeniería de **Nozhgess**. Este documento está diseñado para ser la fuente de verdad absoluta para desarrolladores, auditores y mantenedores del proyecto. Aquí se detalla no solo el *cómo*, sino el *por qué* de cada decisión arquitectónica.

---

## 🏗️ Arquitectura del Sistema

Nozhgess sigue una arquitectura modular híbrida, separando estrictamente la lógica de negocio (Core), la interfaz de usuario (GUI) y la gestión de datos (Data/Config).

### Diagrama de Alto Nivel
```mermaid
graph TD
    User[👤 Usuario] --> GUI[🖥️ Interfaz Gráfica (CustomTkinter)]
    GUI --> Controller[🎮 Controladores (MisionController)]
    Controller --> Config[⚙️ Gestor de Configuración (Mission Config)]
    
    GUI --> Runner[🏃 Runner & Execution Center]
    Runner --> Driver[🤖 SiggesDriver (Selenium)]
    
    Driver --> Web[🌐 SIGGES Web]
    Driver --> Logic[🧠 Lógica de Negocio (Analisis_Misiones)]
    Logic --> Data[📊 Procesamiento de Datos (Pandas)]
```

### Componentes Principales

#### 1. Core (`App/src/core`)
El corazón del sistema.
*   **`Driver.py`**: Wrapper personalizado sobre Selenium WebDriver. Implementa patrones de "Smart One-Wait" y reintentos exponenciales. No es un simple driver; es un agente que entiende el estado de la aplicación web.
*   **`Analisis_Misiones.py`**: Motor de reglas de negocio. Aquí se decide si un paciente es "Habilitado" o "Excluido" basado en las listas de códigos configuradas.
*   **`states.py`**: Definición formal de los estados de la máquina de estados finitos (FSM) que controla la ejecución (IDLE, RUNNING, PAUSED, STOPPING).

#### 2. GUI (`App/src/gui`)
Interfaz moderna construida con `CustomTkinter`.
*   **`views/`**: Vistas principales (Dashboard, Misiones, Log Viewer).
*   **`controllers/`**: Lógica de pegamento que conecta la UI con el Core.
*   **`components/`**: Widgets reutilizables (StatusBadge, LogConsole).

#### 3. Utilidades (`Utilidades/`)
Herramientas de soporte y scripts legacy integrados.
*   **`Mezclador/`**: Módulos para la combinación de documentos y reportes finales.

---

## 🧠 Filosofía de Diseño y Decisiones Clave

### 1. "Smart Waiting" vs "Hard Sleep"
**Problema:** Los `time.sleep()` fijos hacen que el script sea lento en redes rápidas y frágil en redes lentas.
**Solución:** Implementamos `_wait_smart()` en `Driver.py`.
*   **Cómo funciona:** El driver "siente" el DOM. Busca activamente spinners (`dialog.loading`), bloqueos de UI y estados de carga.
*   **Por qué:** Maximiza la velocidad sin sacrificar la estabilidad. Si la página carga en 0.1s, el script avanza en 0.1s.

### 2. Configuración "Viva" (Hot-Reload)
**Problema:** El usuario necesita cambiar reglas (e.g., añadir un código de exclusión) sin reiniciar la aplicación.
**Solución:** `MisionController` y `Mision_Actual.py`.
*   **Cómo funciona:** La configuración se guarda en JSON y se recarga dinámicamente usando `importlib.reload()` antes de cada ejecución.
*   **Por qué:** Permite iteraciones rápidas y correcciones en caliente durante operativos masivos.

### 3. Sistema de Logs Dual (Terminal vs General)
**Problema:** Los logs detallados (debug) son ilegibles para un usuario normal, pero vitales para el desarrollador.
**Solución:** Ruteo de logs en `runner.py`.
*   **Terminal:** Muestra solo lo esencial (Resúmenes, Errores Críticos, Emojis de Estado).
*   **General/Debug:** Registro forense completo de cada clic, espera y decisión lógica.
*   **Implementación:** Un `StreamRedirector` intercepta `stdout` y clasifica los mensajes en tiempo real basado en palabras clave.

---

## 🛡️ Protocolos de Resiliencia (Circuit Breakers)

El sistema opera en entornos médicos críticos donde el fallo no es una opción.

1.  **Protección de Bucle Infinito:**
    *   En `asegurar_en_busqueda`, si la navegación por menú falla, el sistema intenta una navegación directa por URL. Si eso falla, se detiene para evitar "martillar" el servidor.
2.  **Auto-Healing de Configuración:**
    *   Si el usuario (o un editor externo) corrompe el `mission_config.json` (e.g., cadenas dobles `["['val']"]`), el `MisionLoader` detecta la anomalía y la repara automáticamente al cargar.
3.  **Modo "Paranoid" de Verificación:**
    *   Antes de cada acción crítica (clic, envío de formulario), el driver verifica no solo la presencia del elemento, sino que sea `clickable`, visible y que no haya overlays (spinners) obstruyendo.

---

## 🔮 Futuro y Roadmap

### Corto Plazo (v3.1)
*   **Test Suite Automatizado:** Implementar `pytest` para validar las reglas de negocio en `Analisis_Misiones` sin abrir el navegador.
*   **Headless Mode:** Opción para ejecutar sin interfaz gráfica de navegador para servidores.

### Largo Plazo (v4.0)
*   **API Integration:** Si SIGGES abre una API oficial, migrar del Web Scraping a peticiones REST autenticadas.
*   **AI Analysis:** Integrar modelos locales (LLMs pequeños) para interpretar notas clínicas no estructuradas y sugerir códigos.

---

## 📝 Guía de Contribución

1.  **Nunca toques `Mision_Actual` directamente:** Usa el `MisionController`.
2.  **Logs son Sagrados:** Si añades una función nueva, debe tener logs de entrada (DEBUG) y salida (INFO/OK).
3.  **Respetar el Linter:** El código debe ser PEP-8 compliant donde sea posible, priorizando la legibilidad.

---

*Doc generado automáticamente por el equipo de ingeniería de Nozhgess.*
