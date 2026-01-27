# Sistema de Esperas (`Esperas.py`)

## 📌 Propósito y Definición
Este módulo elimina los `time.sleep(5)` arbitrarios.
Provee un **Diccionario Centralizado** (`ESPERAS`) que define exactamente cuánto debe esperar cada acción, con descripciones y categorías.

## ⚙️ Estructura de Datos
Cada espera se define como un objeto:
```python
"search_wait_results": {
    "wait": 2.0,       # Timeout de WebDriverWait (segundos)
    "sleep": 0.0,      # Pausa post-acción (opcional)
    "desc": "Esperar resultados",
    "critical": True   # Si falla, ¿Detener script?
}
```

## 🧠 Filosofía "Zero-Sleep" (Tier SSS+)
La última versión eliminó casi todos los `sleep` fijos.
*   **Antes**: `sleep(0.5)` después de cada click.
*   **Ahora**: `wait: 0.0` y `sleep: 0.0` para navegación rápida, confiando en la detección de spinners.

## ⚠️ Debilidades y Puntos de Falla
1.  **Doble Espera**: A veces el Driver llama a `espera('foo')` Y TAMBIÉN a `WebDriverWait`. Esto es redundante pero seguro.
2.  **Overrides Manuales**: Algunos desarrolladores (o parches rápidos) ignoran este archivo y ponen `time.sleep(1)` directo en el código. Esto hace que ajustar velocidades globales sea imposible.
3.  **Timeouts Falsos**: En PCs muy lentos, `wait: 2.0` podría ser poco para que Chromium renderice un botón, causando falsos positivos de "Elemento no encontrado".

## 📊 Categorías
*   `init`: Arranque del navegador.
*   `login`: Proceso de autenticación.
*   `navigation`: Movimiento entre vistas macro.
*   `search`: Busqueda de pacientes.
*   `mini_table`: Extracción de datos.
