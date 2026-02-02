# 🛠️ DOCUMENTACIÓN BACKEND PROFUNDA: EL SISTEMA NERVIOSO

> **Propósito:** Manual de reparación avanzada para ingenieros.
> **Alcance:** Lógica de `Driver.py`, `core.py` y `Iniciador Web.ps1`.
> **Nivel Técnico:** Hardcore (Requiere saber Python/Selenium).

---

# 1. ARQUITECTURA DE INYECCIÓN (EL "HOOK")

A diferencia de los bots tradicionales que abren su propio navegador, Nozhgess **parasita** una instancia de Edge existente. Esto evita bloqueos de seguridad y permite usar las cookies de sesión del usuario.

## 1.1. El Protocolo de Debugging (CDP)
El archivo `Iniciador/Iniciador Web.ps1` lanza Edge con flags muy específicos:
```powershell
Start-Process msedge.exe "https://www.sigges.cl --remote-debugging-port=9222 --user-data-dir=C:\Selenium\EdgeProfile"
```
*   `--remote-debugging-port=9222`: Abre el puerto JSON de Chrome DevTools.
*   `--user-data-dir=...`: Crea un perfil efímero para no corromper el perfil personal del usuario.

## 1.2. El Handshake en Python (`Driver.py`)
Cuando el usuario da click a "Ejecutar", `Driver.py` hace esto:
```python
opts = webdriver.EdgeOptions()
opts.debugger_address = "localhost:9222"  # Se conecta al puerto abierto por el PS1
driver = webdriver.Edge(..., options=opts)
```
**Punto Crítico:** Si el PS1 no corrió, o si otro proceso ocupó el puerto 9222, esto lanza `WebDriverException: chrome not reachable`.

---

# 2. EL NÚCLEO LÓGICO (`src/core/modules/core.py`)

Aquí yace la inteligencia cinética del robot. No es solo "buscar y clickear".

## 2.1. La Primitiva `_click` (El Click Nuclear)
Esta función es la garantía de estabilidad. Implementa una estrategia de "Tierra Quemada" para asegurar la acción.

**Algoritmo Exacto:**
1.  **Invalidar Caché:** `self._invalidar_cache_estado()`. Evita usar referencias ID viejas (StaleElement).
2.  **TIER SSS+ Sleep:** `time.sleep(1.0)`. **Dato Real:** Esta línea fue solicitada explícitamente para frenar al robot en máquinas lentas. No se negocia.
3.  **Wait Smart:** `self.waits.wait_for_spinner("default")`. Monitoriza `dialog.loading`.
4.  **Búsqueda Resiliente:** Usa `SelectorEngine` con fallbacks (XPath -> ID -> CSS).
5.  **Scroll Táctico:** Ejecuta JS `arguments[0].scrollIntoView({block:'center'});`. Vital para elementos ocultos por headers pegajosos.
6.  **Disparo:**
    *   Intenta `.click()` nativo.
    *   Si falla, usa JS `arguments[0].click()`. (Bypassea overlays transparentes).
7.  **Post-Wait:** Vuelve a chequear spinners.

## 2.2. La Lógica de Conexión Fatal (`es_conexion_fatal`)
El robot monitorea cada excepción contra una lista negra de strings.
Si el error contiene:
*   `"no such window"`
*   `"target window already closed"`
*   `"connection refused"`
*   `"session not created"`
...El sistema declara **MUERTE CEREBRAL**, cierra el hilo y pide reinicio manual. No intenta reconectar automáticamente para evitar bucles infinitos "zombies".

---

# 3. RUTAS CRÍTICAS Y CONFIGURACIÓN

## 3.1. `mission_config.json` (El Cerebro)
Este archivo en `App/config/` dicta el comportamiento.
*   **`MAX_REINTENTOS_POR_PACIENTE`: 5**. Si falla 5 veces (ej: timeout buscando RUT), salta al siguiente.
*   **`indices`:** `{"rut": 1, "nombre": 3, "fecha": 5}`. **Crucial:** Si el Excel de entrada cambia de formato (ej: agregan una columna A nueva), todo se rompe. Aquí se ajusta.
*   **`habilitantes`:** Lista de códigos (ej: `["5002101"]`). Si `Conexiones.py` encuentra este código en la tabla PO de SIGGES, marca la columna en ROJO en el Excel de salida.

## 3.2. `locators.py` (La Biblia de Direcciones)
Centraliza todos los XPaths.
*   Estructura jerárquica: `LOCATORS["login"]["LOGIN_BTN_INGRESAR"]`.
*   Soporta listas de fallback. El driver probará el primero, si falla, el segundo.

---

# 4. SOLUCIÓN DE PROBLEMAS DE BACKEND (DEEP REPAIR)

## Caso 1: "El robot scrollea pero no clickea"
*   **Patología:** Overlay invisible (ej: un aviso de "Sistema en Mantención" transparente).
*   **Cura:** El fallback de JS en `_click` debería manejarlo. Si no, verificar si hay un `iframe` nuevo.

## Caso 2: "TimeoutException en _wait_smart"
*   **Patología:** El Spinner de carga (`dialog.loading`) se quedó pegado aunque la página cargó.
*   **Cura:** Ajustar `ESPERAS["default"]["wait"]` en `App/src/utils/Esperas.py`. (Actualmente 20s). O añadir lógica para ignorar spinner si la URL cambió.

## Caso 3: "ImportError: No module named 'src'"
*   **Patología:** Ejecución incorrecta.
*   **Cura:** Python no encuentra la raíz. Ejecutar siempre desde `Nozhgess.pyw` que configura el `sys.path` antes de importar nada.

---
**Este documento desnuda la lógica interna para una mantención precisa.**
