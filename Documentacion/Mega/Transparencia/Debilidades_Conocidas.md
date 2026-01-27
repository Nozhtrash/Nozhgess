# Reporte de Debilidades y Vulnerabilidades (Honestidad Brutal)

## 📌 Propósito
Este documento expone **todo lo malo** del proyecto. Sin filtros.
Conocer estas debilidades es vital para no romper el script en futuros cambios.

## 💀 Vulnerabilidades Críticas

### 1. El "Infierno de Versiones" de la GUI
*   **Problema**: En `App/src/gui/` existen `enhanced_app.py`, `final_app.py`, `ultra_optimized_app.py`.
*   **Riesgo**: Un desarrollador junior podría editar `enhanced_app.py` pensando que mejora la app, pero `Nozhgess.pyw` solo carga `app.py`.
*   **Estado**: Deuda técnica severa.

### 2. Dependencia del Puerto 9222
*   **Problema**: El script asume *ciegamente* que Edge está corriendo en el puerto 9222.
*   **Riesgo**: Si el usuario abre Edge normal (doble click), ocupa otro puerto. El script dirá "No connection" y fallará.
*   **Mitigación**: Usar siempre `Iniciador Web.ps1`.

### 3. Fragilidad de Selectores (DOM Drift)
*   **Problema**: `Direcciones.py` tiene algunos selectores absolutos (`/html/body/div/main...`).
*   **Riesgo**: Si SIGGES agrega un `<div>` extra en el layout, estos selectores dejarán de funcionar.
*   **Impacto**: Alto. Requiere mantenimiento constante si la web cambia.

### 4. La Trampa de la "Tabla Vacía"
*   **Problema**: En `Mini_Tabla.py`, una tabla vacía (sin casos) se ve igual a una tabla que *aún no carga*.
*   **Riesgo**: Race condition. Si el script es más rápido que el internet del hospital, puede reportar "Sin caso" falsamente.
*   **Mitigación**: Se usan esperas (`Wait`), pero nunca es 100% seguro en redes terribles.

## ⚠️ Deuda Técnica y "Code Smells"

### 1. Estructura de Carpetas Confusa
*   El código hace `from Z_Utilidades...` pero la carpeta física a veces es `Utilidades` o `App/src/utils`.
*   `Iniciador Script.py` hace magia negra con `sys.path` para que los imports funcionen. Mover un archivo de lugar romperá todo.

### 2. Sobrescritura de Configuración
*   La GUI modifica `Mision_Actual.py` reescribiendo el archivo de texto.
*   Si la GUI tiene un bug al escribir, corrompe el archivo `.py` y el script deja de iniciar (`SyntaxError`).

### 3. Logs "Excesivos"
*   En modo DEBUG, la consola imprime gigabytes de texto.
*   `Terminal.py` tiene parches para evitar crasheos por emojis en Windows (`safe_print`).

## 🔍 Conclusión
El sistema es **Robusto en Lógica** (maneja bien los casos médicos), pero **Frágil en Infraestructura** (depende de que el entorno sea perfecto: puerto 9222, rutas exactas, internet estable).
