# Detector Inteligente de Archivos (`App/src/utils/smart_file_detector.py`)

## 📌 Propósito
Soluciona el problema de "Usuario tiene que copiar ruta manualmente".
El script busca archivos Excel en lugares probables (`Downloads`, `Desktop`, `OneDrive`) y los clasifica por relevancia.

## 🧠 Heurística de Puntuación (`_calculate_file_score`)
Cada archivo encontrado recibe un puntaje (0-100) para ordenar los resultados:
*   **Base**: 50 puntos.
*   **Recencia**:
    *   < 24 horas: +30 ptos.
    *   < 7 días: +20 ptos.
*   **Nombre Relevante**: Si contiene "tamizaje", "medico", "revisión": +15 ptos.
*   **Tamaño**: +1 punto por cada MB (max 20).

## 🔍 Estrategias de Búsqueda
1.  **Common Paths**: Escanea carpetas estándar de Windows.
2.  **Specific Hint**: Si `Mision_Actual.py` tiene una ruta vieja, intenta buscar *ese mismo nombre de archivo* en otras carpetas.
3.  **User Preference**: Recuerda la última elección del usuario en `AppData/Local/Nozhgess/file_preferences.json`.

## 🖥️ Interfaz de Selección (`tkinter`)
Si hay múltiples candidatos, muestra un diálogo gráfico moderno (fondo oscuro) permitiendo elegir.
*   Si no encuentra nada, ofrece botón "Buscar Manualmente".
