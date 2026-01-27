# Sistema de Debug y Diagnóstico Profesional (`DebugSystem.py`)

## 📌 Propósito y Definición
Un sistema de logging multinivel diseñado para **trazabilidad total**.
Permite ver desde "Qué paciente falló" (Nivel INFO) hasta "Cuántos milisegundos tomó leer el RUT" (Nivel TRACE).

## 🎚️ Niveles de Verbosidad
1.  **CRITICAL (0)**: El mundo se acaba.
2.  **ERROR (1)**: Algo falló, pero seguimos.
3.  **INFO (2)**: "Procesando paciente X". (Default producción).
4.  **DEBUG (3)**: "Entrando a función Y con params Z".
5.  **TRACE (4)**: Firehose. Loguea cada línea. Úsalo con cuidado.

## 🚀 Performance Tracking
Incluye decoradores para medir tiempos automáticamente:
*   `@debug.trace_function`: Loguea cuándo entra y sale una función, y cuánto demoró.
*   Colorea el tiempo en consola: **Verde** (<100ms), **Amarillo** (<1s), **Rojo** (>1s).

##  context managers
```python
with DebugBlock("Analizando Habilitantes", caso=123):
    # Todo lo que pase aquí dentro se loguea agrupado
```
Esto genera logs visualmente indentados y fáciles de leer.

## ⚠️ Impacto en Rendimiento
En nivel `TRACE`, el script es **10-20% más lento** debido a la cantidad de E/S en consola.
Para producción máxima velocidad, usar nivel `INFO`.
