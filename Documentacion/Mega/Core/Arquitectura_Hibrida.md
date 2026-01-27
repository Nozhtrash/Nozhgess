# Arquitectura Híbrida y Capa de Integración

## 📌 El Desafío
Nozhgess evolucionó de un script monolítico (`Iniciador Script.py`) a una aplicación moderna (`App/src`).
El reto fue: **¿Cómo hacer que la GUI moderna controle el motor antiguo sin reescribir todo el código legacy?**

## 🧩 La Solución: "Universal Compatibility Layer"
Ubicada en `App/src`, esta capa actúa como un traductor diplomático entre los dos mundos.

### 1. `universal_compatibility.py`
El "Camaleón" del sistema.
*   **Detección de Modo**: Sabe si se está ejecutando desde la GUI (`customtkinter`), desde una terminal (`CLI`) o desde VSCode (`IDE`).
*   **Inyección de Paths**: Manipula agresivamente `sys.path` para que los imports legacy (`from Z_Utilidades...`) funcionen aunque el archivo esté en `App/src`.
*   **Unified Logging**: Redirige los `print()` antiguos a los nuevos logs estructurados.

### 2. `smart_runner.py`
El "Buscador Inteligente".
*   **Problema Antiguo**: El usuario tenía que escribir la ruta exacta `C:\Users\...\archivo.xlsx`.
*   **Solución Nueva**: Este módulo escanea automáticamente Escritorio, Documentos y Descargas buscando Excels válidos.
*   **Configuración Volátil**: Modifica `Mision_Actual.py` (o su equivalente JSON) *on-the-fly* antes de lanzar el motor.

### 3. `integrator.py`
El "Pegamento".
*   Importa funciones del `Core` antiguo y las expone como objetos limpios para la GUI.
*   Maneja las excepciones del Core (que suelen ser crudas) y las presenta como mensajes de error amigables en la ventana de la App.

## ⚠️ Riesgos de esta Arquitectura
1.  **Fragilidad de Imports**: Si mueves un archivo en `Utilidades`, `universal_compatibility.py` podría fallar al intentar inyectarlo.
2.  **Doble Configuración**: A veces la GUI cree que la configuración es X, pero el archivo `Mision_Actual.py` en disco dice Y. El Runner intenta sincronizarlos, pero pueden ocurrir condiciones de carrera.
3.  **Logs Duplicados**: A veces verás un log en formato antiguo y otro en formato nuevo para el mismo evento.

## 🔮 Futuro
La meta es que el `Core` eventualmente sea absorbido por `App/src` y esta capa de compatibilidad desaparezca. Pero por ahora, es el puente que mantiene el barco a flote.
