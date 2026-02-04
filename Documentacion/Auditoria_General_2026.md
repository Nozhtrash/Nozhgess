# Auditoría Técnica del Proyecto Nozhgess

**Fecha:** 2026-02-03
**Versión Auditada:** Nozhgess original

## 1. Resumen Ejecutivo
El proyecto presenta una arquitectura híbrida que combina una base de código moderna (`App/src`) con módulos heredados (`Utilidades`, `Z_Utilidades`). Aunque funcional, esta estructura introduce complejidad en el mantenimiento, dispersión de la lógica de negocio y riesgos de integridad de datos debido a la sincronización manual de configuraciones.

## 2. Análisis Estructural

### 2.1. Dispersión de Módulos (Separation of Concerns)
Se detectaron tres (3) núcleos de lógica que deberían estar unificados:

1.  **`App/src/` (Moderno)**: Contiene la GUI (`App/src/gui`), utilidades nuevas y lógica de integración. Sigue buenas prácticas de estructura.
2.  **`Utilidades/Mezclador/` (Legacy Crítico)**: Contiene `Conexiones.py`, que es el **corazón del procesamiento**. Es inusual que el core resida en una carpeta llamada "Utilidades".
3.  **`Z_Utilidades/` (Motor Base)**: Contiene drivers de Selenium (`Motor/Driver.py`) y utilidades generales (`Principales`). El prefijo "Z_" sugiere una intención de ordenamiento visual en explorador de archivos más que semántico.

**Observación Crítica:** La dependencia cruzada entre `App/src` (GUI) y `Utilidades/Mezclador` (Lógica) a través de imports relativos o manipulación de `sys.path` es un punto de fragilidad.

### 2.2. Archivos en Raíz
Existen archivos que deberían ser limpieza u organizados:
- ⚠️ `actualizar_folio_vih.py`: Posiblemente un script "one-off" que quedó olvidado.
- ⚠️ `runner_methods_temp.py`: Archivo temporal que debería eliminarse.
- ⚠️ `Biblia Direcciones.txt`: Archivo de datos crítico (XPaths) en formato texto plano en raíz. Debería ser un JSON/YAML de configuración o un módulo `constants.py`.
- ⚠️ `Validaciones.py`: Existe en Raíz y en `App/`. Posible duplicación.

## 3. Integración y Compatibilidad

### 3.1. Gestión de Configuración (El Problema de los Dos Mundos)
El sistema utiliza un mecanismo de "Hot Reload" y sincronización bidireccional para mantener compatibles el Frontend y el Backend:
- **Frontend** usa `App/config/mission_config.json`.
- **Backend Legacy** usa `Mision_Actual.py` (módulo Python).
- **Mecanismo:** `MisionController` escribe el JSON y fuerza recarga de variables.
- **Riesgo:** Si el formato de `Mision_Actual.py` cambia o se corrompe (error de sintaxis al generar el archivo), el backend fallará silenciosamente o con errores de importación.

### 3.3. Configuración Hardcoded (Riesgo Alto)
Se inspeccionó `App/config/mission_config.json` y se encontraron rutas absolutas dependientes del usuario:
- `C:/Users/knoth/...`
- **¡ALERTA!:__ `C:/Users/usuariohgf/...` (Ruta de otro usuario, probablemente romperá la ejecución si se intenta usar esa misión).
Esto hace que el proyecto no sea portable entre equipos sin reconfiguración manual masiva.

### 3.4. Dependencias (`requirements.txt`)
Existen dos archivos de requerimientos con conflictos de versiones:
- `App/requirements.txt`: Solicita `selenium>=4.40.0` (Versión inexistente o futura, probablemente error tipográfico) y paquetes modernos (`customtkinter`).
- `Utilidades/requirements.txt`: Solicita `selenium>=4.0.0,<5.0.0` (Más conservador).
**Acción Recomendada:** Unificar un solo `requirements.txt` en la raíz.

## 4. Frontend (GUI)
- Uso de `customtkinter` (moderno).
- `control_panel_legacy.py`: Puente al mundo legacy.
- **Validación:** Se confirmó que la GUI escribe correctamente en `mission_config.json`, pero perpetúa el uso de rutas absolutas si el usuario las selecciona con el selector de archivos.

## 5. Backend (Core)
- `Conexiones.py`: Archivo monolítico (`1600+` líneas).
  - Maneja: Lectura de Config, Selenium, Lógica de Negocio, Excel de Salida.
  - **Imports:** Importa masivamente de `Mision_Actual`, acoplándose a la configuración global.
  - **Code Smell:** Depende de que `sys.path` esté manipulado desde `Nozhgess.pyw`.

## 6. Archivos en Raíz (Limpieza)
- `actualizar_folio_vih.py`: Script ad-hoc. **Recomendación: Mover a `Scripts/` o borrar.**
- `runner_methods_temp.py`: Temporal. **Recomendación: Borrar.**
- `Validaciones.py`: Duplicado en `App/`. **Recomendación: Borrar el de raíz.**
- `Biblia Direcciones.txt`: Documentación valiosa pero no usada por el código (que usa `locators.py`). **Recomendación: Mover a `Documentacion/`.**

## 7. Conclusión General
El proyecto es funcional y cuenta con características avanzadas (Hot Reload, GUI dinámica), pero sufre de una "Deuda Técnica Arquitectónica" debido a la coexistencia de dos estructuras (Vieja vs Nueva).
La implementación de las nuevas características (VIH, Contra) fue exitosa y sigues los patrones existentes, pero el cimiento sobre el que descansan es frágil ante cambios de entorno.

**Estado de Implementación (VIH / Contra):** 100% Funcional y Verificado.
**Estado del Proyecto General:** Funcional pero requiere Refactorización de Estructura para mantenibilidad a largo plazo.
