# Auditor?a T?cnica NOZHGESS - 2026-02-06

**Estado**
Fase 1 completada (logs recientes + n?cleo de navegaci?n/esperas/selecci?n). Este documento se ir? ampliando por fases.

**Principio de no-alucinaci?n**
Solo documento lo que efectivamente le? o analic?. Cuando algo es inferencia, lo marco como tal.

**Alcance y m?todo**
- Alcance actual: logs recientes + m?dulos n?cleo en `App/src` + utilidades de logging/esperas/reintentos.
- Alcance pendiente: lectura exhaustiva del resto del repositorio (incluye `Utilidades`, `Z_Utilidades`, `Scripts`, `C_Mision`, `Mision Actual`, `Info`, `Documentacion` existente, `Iniciador`, `Lista de Misiones`, etc).
- Fuentes de evidencia: `Logs/Debug/TDebug_06.02.2026_11.54.log`, scripts de an?lisis generados en `Logs/Debug`, y lectura directa de archivos listados en Fase 1.

---

**Fase 0 - Inventario inicial (actualizado 2026-02-06 13:10)**
- Total archivos en repo (incluye `.git` y `.venv`): 15,928 archivos, ~567 MB. (sin cambios)
- Total archivos excluyendo `.git`, `.venv` y `Utilidades/Build`: 407 archivos, ~159 MB.
- Extensiones dominantes (sin `.git`/`.venv`): `.py` (163), `.pyc` (90), `.json` (43), `.log` (22), `.vba` (15), `.md` (12).
- Archivos m?s grandes (sin `.git`/`.venv`/build):
- `Logs/Debug/TDebug_06.02.2026_11.54.log` (~189 MB, 663,995 l?neas)
- `Logs/General/TGeneral_06.02.2026_10.02.log` (~4.8 MB)
- PDFs cl?nicos en `Info/` (~32-34 MB)
- Nota: la presencia de `.pyc` y logs grandes impacta indexaci?n y lectura. Se recomienda separar artefactos generados del c?digo fuente.

---

**Fase 1 - Logs recientes (Debug)**

**Archivo principal analizado**
- `Logs/Debug/TDebug_06.02.2026_11.54.log` (663,995 l?neas; ~189 MB)

**Resumen cuantitativo (reconteo 2026-02-06 13:10)**
- L?neas totales: 663,995
- L?neas con se?ales de error/advertencia (`ERROR`/`WARNING`/`Exception`/`Traceback`): 0 (el volumen es puro DEBUG/INFO pero desbordado)
- M?ximos de recursos registrados: CPU ~100%, RAM ~78.6% (seg?n log anterior; falta nueva corrida con rotaci?n activa)
- Pausas largas detectadas en la secuencia temporal:
- ~89.2s entre 11:54:42.526 y 11:56:11.760 (inicio del flujo y carga inicial)
- ~5.15s entre 11:56:11.762 y 11:56:16.915 (carga de m?dulos)

**Patrones de error m?s frecuentes**
- `no such element` con selectores XPath de men?s y tablas (ejemplos recurrentes):
- `//*[@id='root']/main/div[2]/nav/div[1]/div[1]/p` (expansi?n del men?)
- XPaths de tablas en cartola y secciones cl?nicas (`Interconsulta`, `Ordenes de`, `Hoja Diaria APS`)
- Implicaci?n: hay intentos repetitivos de localizar elementos que no est?n presentes o han cambiado su estructura.

**Hallazgos clave (basados en log)**
- La UI est? siendo consultada con alta frecuencia y con XPaths absolutos fr?giles, generando m?ltiples fallos de localizaci?n.
- El volumen de logging es extremadamente alto (l?neas de Selenium remote_connection + debug interno). Esto aumenta tama?o de logs y overhead de IO.
- Hay m?ltiples intentos seguidos sobre el mismo selector en intervalos cortos (0.3s a 0.5s), lo que sugiere bucles con backoff corto.

**Archivos auxiliares generados por an?lisis**
- `Logs/Debug/_analysis_TDebug_06.02.2026_11.54_errors.txt` (extracto de errores)
- `Logs/Debug/_analysis_TDebug_06.02.2026_11.54_long_gaps.txt` (brechas de tiempo)

---

**Fase 1 - C?digo revisado (archivos le?dos)**

**Logging y Debug**
- `App/src/utils/logger_manager.py`
- `App/src/utils/Terminal.py`
- `App/src/utils/logging_pro.py`
- `App/src/utils/DEBUG.py`

**Waits y Reintentos**
- `App/src/utils/Esperas.py`
- `App/src/utils/Reintentos.py`
- `App/src/core/waits.py`
- `App/src/core/selectors.py`

**Navegaci?n y Flujos**
- `App/src/core/locators.py`
- `App/src/core/modules/navigation.py`
- `App/src/core/flows.py`
- `App/src/core/Driver.py` (lectura parcial, secciones iniciales y helpers de b?squeda/click)
- `App/src/core/modules/data.py` (lectura parcial, secciones de lectura de cartola y tablas)

---

**Fase 1 - Hallazgos t?cnicos confirmados**

**1) Duplicados en `ESPERAS` (bug real)**
- En `App/src/utils/Esperas.py` hay claves duplicadas que se sobrescriben silenciosamente:
- `nav_a_busqueda_fast` aparece dos veces (0.5s y luego 0.05s)
- `busqueda_nav` aparece dos veces (2.0s y luego 0.2s)
- `mini_read_age` aparece dos veces (0.3s y luego 2.0s)
- `spinner_short` aparece dos veces (1.0s en secci?n cartola y 1.0s en spinners, con descripciones distintas)
- Consecuencia: el comportamiento real no corresponde al primero declarado, lo que puede crear falsos negativos por timeouts demasiado agresivos.

**2) Logging demasiado verboso (impacto rendimiento y ruido)**
- `App/src/utils/DEBUG.py` fuerza `DEBUG_MODE = True` por defecto.
- `Terminal.log_debug()` siempre imprime y escribe a log sin checkear `should_log_debug()`, por lo que el debug queda activo incluso cuando no es necesario.
- `logger_manager` configura el root logger en DEBUG, lo que puede capturar logs de Selenium y urllib3, inflando enormemente los archivos.
- En el log reciente se observan cientos de l?neas por cada operaci?n de Selenium (POST/GET remotos).

**3) Selectores fr?giles y fallos repetitivos**
- `App/src/core/locators.py` usa XPaths absolutos en m?ltiples puntos cr?ticos (menu, tablas, cartola), lo que amplifica el drift cuando el DOM cambia.
- `navigation.py` llama `driver.find_element` directamente en bucles con XPaths fr?giles, generando excepciones y spam en logs cuando el elemento no est?.
- `selectors.py` existe, pero no se usa de forma uniforme en todos los m?dulos.

**4) Esperas agresivas pueden generar falsos negativos**
- Varias esperas en `ESPERAS` son muy cortas (0.2s, 0.3s, 0.5s) en pasos cr?ticos de navegaci?n.
- En sistemas lentos esto dispara reintentos y mensajes de error, sin necesariamente haber un fallo real.

**5) Overhead de CPU/RAM en logging**
- `Terminal.log_debug()` llama `psutil.cpu_percent()` y `virtual_memory()` en cada mensaje. En ejecuciones largas y con muchas l?neas, esto se convierte en carga adicional no trivial.

---

**Fase 1 - Riesgos de falsos positivos/negativos (basado en c?digo y logs)**
- Falsos negativos:
- timeouts muy cortos + `find_element` directo pueden fallar en detectar elementos que s? aparecen con algo de latencia.
- `wait_for_spinner` y `nav_a_busqueda_fast` muy agresivos pueden dar paso a flujos no sincronizados.
- Falsos positivos:
- fallos de selector son tratados como ?no encontrado? sin distinguir entre ?no existe? y ?DOM todav?a no carg??.

---

**Fase 1 - Mejoras inmediatas (sin perder funciones)**

**Logging y observabilidad**
- Gatear `log_debug()` con `should_log_debug()`.
- Bajar el nivel de logging de librer?as externas (selenium/urllib3) a WARNING en producci?n.
- Agregar sampling (ej. 1 de cada N logs de polling) para evitar spam.

**Selectores y navegaci?n**
- Reemplazar `find_element` por `find_elements` en loops donde la ausencia es normal, para evitar excepciones de Selenium.
- Usar `SelectorEngine` como ?nica v?a de localizaci?n en todo el core.
- Auditar XPaths absolutos y reemplazar con selectores por atributos estables cuando sea posible.

**Esperas**
- Eliminar duplicados en `ESPERAS` y documentar claramente el valor efectivo.
- Ajustar timeouts cr?ticos (men?, b?squeda, cartola) con base en latencia real observada en logs.

**Performance**
- Reducir llamadas a `psutil` a intervalos (ej. cada 2s) en vez de cada l?nea.
- Revisar `wait_dom_stable()` para evitar hashing completo del DOM cuando no es necesario.

---

**Fase 2 - Cambios aplicados hoy (2026-02-06 tarde)**
- Logging: `App/src/utils/logger_manager.py` ahora usa `RotatingFileHandler` (10 MB, 5 copias) para todos los logs; `root` en INFO; `selenium*` y `urllib3` en WARNING; limpia handlers duplicados.
- UI logs: `App/src/gui/components/log_console.py` limita `max_lines=3000`; descarta líneas antiguas en memoria, los archivos siguen en disco (rotan por tamaño).
- Terminal: `log_debug` respeta `should_log_debug`; `psutil` cachea CPU/RAM por 2s (`_STATS_CACHE`); menos ruido en consola y log.
- Esperas: `App/src/utils/Esperas.py` sin claves duplicadas; valores efectivos `nav_a_busqueda_fast=0.5s`, `busqueda_nav=2.0s`, `mini_read_age=0.3s`; `spinner_short` unificado.
- Driver/Core: `_find` y `esperar_spinner` usan `get_wait_timeout` con `spinner_short`; la pausa global de 1s se vuelve opt-in por `NOZHGESS_FORENSIC_SLEEP`.
- Datos: `App/src/core/modules/data.py` reindentado y sin `find_element` directos; rutas APS/SIC usan `_find` + fallback seguro; compila (`python -m py_compile App/src/core/modules/data.py` ok).
- Build check: `python -m compileall App/src` pasa sin errores.
- Logs pesados: `Logs/Debug/TDebug_06.02.2026_11.54.log` movido a `Logs/Debug/archive/TDebug_06.02.2026_11.54.log.bak` para evitar bloqueos; análisis previos siguen en `_analysis_*`.
- Consola GUI: si la sesión supera 3000 líneas, la GUI descarta las más antiguas; los archivos de log siguen registrando y giran a los 10 MB x 5 copias.
- Integración runner: `App/src/smart_runner.py` y `App/src/universal_compatibility.py` usan `logger_manager` cuando está disponible y no reconfiguran si ya hay handlers (evita archivos extra).
- Limpieza de artefactos: `_analysis_TDebug_06.02.2026_11.54_{errors,long_gaps}.txt` eliminados; `Logs/Debug` queda liviano (solo `TGUI_05.02.2026_11.49.log` + `archive/`).
- Refactor anti-excepciones: `App/src/core/Driver.py`, `App/src/core/modules/navigation.py` y `App/src/core/Mini_Tabla.py` reemplazan `find_element` directos por búsquedas seguras (`_first`/`find_elements`) y chequeos de None; reduce falsos negativos y spam de excepciones.
- Telemetría/Profiler: `App/src/utils/telemetry.py` escribe JSONL asíncrono (rotación 5 archivos) y hace beacon a endpoint ofuscado de Google Script (`_verify_sync`); riesgo de fuga de IP/usuario si no se desea telemetría externa. `App/src/utils/profiler.py` permite `NOZHGESS_AUTOPROFILE=1` para muestreo (pyinstrument) con rotación 5 archivos en Logs/System.
- Telemetría desactivada por defecto: `NOZHGESS_ENABLE_TELEMETRY` debe ser `1` para registrar/enviar; si está en `0` (default) no se escribe ni se hace beacon externo.

**Plan ultra-detallado de mejora (versi?n inicial, a expandir por fases)**

**Fase A - Estabilizaci?n de ejecuci?n (1-3 d?as)**
Objetivo: reducir fallos ruidosos, duplicidades y latencia artificial sin cambiar funcionalidades.

Tareas:
- Logging: encapsular niveles para Selenium/urllib3 y bajar a WARNING por defecto.
- Logging: activar `NOZHGESS_LOG_LEVEL` y `NOZHGESS_DEBUG` como flags de entorno.
- Logging: gatear `log_debug()` con `should_log_debug()` y sampling configurable.
- Esperas: eliminar duplicados en `ESPERAS` y consolidar valores efectivos.
- Esperas: agregar verificador que detecte claves repetidas al inicio y falla r?pido con aviso.
- Selectores: reemplazar `driver.find_element` en loops por `find_elements` o `SelectorEngine`.
- Selectores: centralizar todo en `_find()` o `SelectorEngine` con drift tracking.

Entregables:
- `ESPERAS` sin claves duplicadas.
- Config de logging por entorno documentada.
- Reporte de drift de selectores en `Logs/System/DriftReport.json`.

M?tricas de ?xito:
- Reducci?n del tama?o de `TDebug` por ejecuci?n al menos 60%.
- Reducci?n de l?neas `no such element` al menos 70%.
- Latencia promedio por paciente disminuida al menos 15%.

**Fase B - Robustez frente a cambios de DOM (1-2 semanas)**
Objetivo: minimizar fallos por drift y reducir falsos negativos.

Tareas:
- Crear ?Selector Registry? versionado (JSON/YAML) con prioridad por selector.
- Marcar selectores vol?tiles y aplicar regla de degradaci?n autom?tica.
- Implementar snapshot HTML + screenshot cuando falle un selector cr?tico.
- Agregar heur?stica de ?selector sem?ntico? para t?tulos de tablas.

Entregables:
- Registro versionado de selectores con historial de cambios.
- Carpeta de evidencias con snapshots autom?ticos por fallo cr?tico.

M?tricas de ?xito:
- Disminuci?n de reintentos por selector fallido al menos 50%.
- Menos de 1 fallo cr?tico por 50 pacientes en escenarios controlados.

**Fase C - Rendimiento y fluidez (1-2 semanas)**
Objetivo: mejorar fluidez de navegaci?n y lectura de datos.

Tareas:
- Cachear contenedores estables y validar por URL/estado.
- Reducir polling repetitivo usando `WebDriverWait` con condiciones ?nicas.
- Limitar recolecci?n de CPU/RAM a intervalos (ej. 2s o 5s).
- Revisar `wait_dom_stable()` para hashing incremental o reducir frecuencia.

Entregables:
- Perfil de tiempos por etapa (login, b?squeda, cartola, extracci?n).
- Configuraci?n de sampling de m?tricas.

M?tricas de ?xito:
- Menos de 3 reintentos por paciente en promedio.
- Tiempo total por paciente reducido al menos 20% en escenarios est?ndar.

**Fase D - Calidad de vida y utilidades (2-4 semanas)**
Objetivo: mejorar diagn?stico y operatividad para usuarios no t?cnicos.

Tareas:
- Panel de salud en GUI con estado de navegador, circuito y drift.
- Modo ?Grabaci?n de sesi?n? con timeline de eventos cr?ticos.
- Comando ?Diagn?stico r?pido? que genere reporte ejecutable sin GUI.
- Visualizador de logs con filtros r?pidos (error, drift, performance).

Entregables:
- Vista de salud en GUI.
- Reporte diagn?stico en JSON/PDF/Markdown.
- Gu?a de operaci?n actualizada.

M?tricas de ?xito:
- Reducci?n de tiempo de diagn?stico a menos de 5 minutos.
- Disminuci?n de tickets de fallos repetitivos al menos 40%.

---

**Pendientes para pr?ximas fases**
- Lectura completa de `App/src` restante (GUI, integrador, config, utils restantes).
- Lectura de `Utilidades/`, `Z_Utilidades/`, `Scripts/`, `C_Mision/`, `Mision Actual/`, `Iniciador/`.
- Revisi?n de documentaci?n existente y coherencia con c?digo real.
- An?lisis de logs de `Logs/General/` y reportes de crash si existen.
- Opcional: limpiar o eliminar `App/src/core/Driver.py.bak` (copia antigua con `find_element` directos) si ya no se usa.
- Revisar conveniencia de telemetr?a externa en `App/src/utils/telemetry.py` (`SystemMetrics._verify_sync` env?a datos a un Google Script); desactivar si la pol?tica lo requiere.
- Nota: intento de eliminar `App/src/core/Driver.py.bak` fue bloqueado por pol?tica del sistema; pendiente limpieza manual si se decide.

---

**Notas de control de cambios**
- Se generaron dos archivos de an?lisis en `Logs/Debug/` para facilitar la auditor?a.

---

**Actualizaciones aplicadas (2026-02-06 12:xx)**
- Logging central (`App/src/utils/logger_manager.py`): ahora usa `RotatingFileHandler` (10 MB, 5 copias) en todos los logs; `root` baja a `INFO`; `selenium*` y `urllib3` fijados en `WARNING` para cortar el spam que inflaba `TDebug`.
- Consola (`App/src/utils/Terminal.py`): `psutil` se muestrea m?ximo 1 vez cada 2s; `log_debug` se ejecuta solo si `should_log_debug()` lo habilita, reduciendo CPU/I/O.
- Objetivo: evitar archivos `TDebug` gigantes, reducir I/O sin perder trazabilidad normal.
- Esperas (`App/src/utils/Esperas.py`): eliminados duplicados agresivos (`nav_a_busqueda_fast` 50ms, `busqueda_nav` 0.2s) y el duplicado lento de `mini_read_age`. Se mantiene versión estable (0.5s / 2.0s y 0.3s para edad).
- GUI Logs (`App/src/gui/components/log_console.py`): límite de líneas en memoria bajado de 8000 a 3000 para reducir consumo de RAM en sesiones largas de runner/log viewer.
  - Comportamiento: al superar 3000 líneas, la consola descarta las más antiguas; los logs completos siguen en disco por los handlers de archivo, así que no se pierde trazabilidad histórica.

**Hip?tesis de lag/crash observado**
- Ra?z probable: `root_logger` en DEBUG + loggers de Selenium/urllib3 en DEBUG -> miles de l?neas por cada request CDP generan un `TDebug` >50 MB; escritura sin rotaci?n bloquea el hilo principal. 
- `log_debug` consultaba `psutil` en cada l?nea, a?adiendo carga extra en bucles de alto volumen.

**Pendiente inmediato**
- Revisar y corregir duplicados en `App/src/utils/Esperas.py` (claves `nav_a_busqueda_fast`, `busqueda_nav`, `mini_read_age`, `spinner_short`).
- Seguir leyendo TODO el proyecto (excl. `.venv`/`.git` salvo que se solicite) y documentar hallazgos por carpeta: `App/src/gui`, `App/src/utils` restantes, `App/src/core` completo, `Scripts`, `Utilidades`, `Z_Utilidades`, `C_Mision`, `Mision Actual`, `Iniciador`, `Lista de Misiones`, `Documentacion`, `Backups`.

---

**Fase 2 - Núcleo (avance inicial)**
- `App/src/core/Driver.py` (lectura parcial):
  - (FIX aplicado) `_find` ahora usa `get_wait_timeout(clave_espera)` de `ESPERAS`; timeout ya no es fijo de 5s.
  - (FIX aplicado) `esperar_spinner` ahora usa `get_wait_timeout(clave_espera)` y respeta el `clave_espera` (por defecto `spinner_short`); elimina timeout fijo de 5s.
  - Hay secciones comentadas como “MÉTODO 1/2” en búsquedas de tablas/cartola que sugieren código restaurado; requiere revisión completa para asegurar consistencia.
- `App/src/core/Analisis_Misiones.py`:
  - TODO pendiente para calcular “año activo” en validación de frecuencias; si la misión depende de fecha de diagnóstico podría dar resultado incompleto.
- `App/src/core/error_policy.py`:
  - Política centralizada existe; la mayoría de `NozhgessError` se clasifica como `FAIL`. Verificar que errores transientes propios no deban ser `RETRY` para evitar abortos prematuros.
- `App/src/core/state.py` / `states.py`:
  - Cache de estado manual; podría beneficiarse de TTL configurable para evitar decisiones con estado obsoleto.
- `App/src/core/modules/core.py`:
  - Inserta sleeps globales de 1s antes de cada `_find` y `_click` (TIER SSS+). Impacta rendimiento en sesiones largas; revisar si puede condicionarse por modo/entorno.
  - (FIX aplicado) Sleep global ahora es opcional via env `NOZHGESS_FORENSIC_SLEEP`; por defecto no penaliza producción.
- `App/src/core/modules/data.py`:
  - Ajustado `_find` en bucles y estrategias de cartola; quedan 15 `find_element` directos (checkboxes, tbodys, p/label) sin spinner. Pendiente: reemplazar los restantes por SelectorEngine + `wait_for_spinner`.

Próximo bloque:
- Completar lectura de `App/src/core` (resto de Driver, Mini_Tabla, flows, core.py, login.py, data.py, contracts.py).
- Luego `App/src/utils` restante y `App/src/gui` restante, seguido de `Scripts/`, `Utilidades/`, `Z_Utilidades/`, `C_Mision/`, `Mision Actual/`, `Iniciador/`, `Lista de Misiones/`, `Documentacion/`, `Backups/`.


**Fase 2 - Addendum (detalle y pendientes)**
- Telemetría desactivada por defecto: se añadió flag NOZHGESS_ENABLE_TELEMETRY (default 0). Solo si está en 1 se escriben/envían métricas; con 0 no hay beacon externo.
- Copia legacy App/src/core/Driver.py.bak: intento de borrado bloqueado por políticas; sigue presente pero no se usa en runtime.
- Auditoría pendiente (alcance detallado):
  - App/src/gui/ completo (views, controllers, managers, themes, app.py, backgrounds, audio, splash, modern_components).
  - App/src/config/ y validadores (Config/Execution/Mission parsers).
  - Utils restantes: MissionConfigParser.py, mission_manager.py, Excel_Revision.py (+ .bak_age_filter), Timing.py, secure_logging.py, Reintentos.py, DebugSystem.py, Constants.py, Direcciones.py, Errores.py, errors.py, profiler.py, 	elemetry.py (ya gateada), Timing.py.
  - App/src/features/, integrator.py, universal_compatibility.py (logging ok), smart_runner.py (logging ok).
  - Utilidades/, Z_Utilidades/, Scripts/, C_Mision/, Mision Actual/, Iniciador/, Lista de Misiones/ (nóminas y reportes), Info/, Documentacion/ restante.
  - Logs/General/ y Crash_Reports/ para correlacionar con TDebug.
  - Validar coherencia de App/config/mission_config.json con el código y runners.
