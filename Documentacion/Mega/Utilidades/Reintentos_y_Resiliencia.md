# Sistema de Reintentos y Resiliencia (`Reintentos.py`)

## 📌 Propósito y Definición
Implementa patrones de diseño "Enterprise" para que el script no se caiga cuando el internet del hospital parpadea.
Inspirado en librerías como Resilience4j.

## 🧠 Componentes Clave

### 1. `CircuitBreaker` (Cortacorrientes)
*   **Concepto**: Si fallan 5 pacientes seguidos, algo grave pasa (SIGGES caído, IP bloqueada).
*   **Acción**: El circuito se "Abre" y rechaza reintentos inmediatos para no saturar el servidor ni perder tiempo.
*   **Estados**: `CLOSED` (Normal) -> `OPEN` (Fallo masivo) -> `HALF_OPEN` (Probando recuperación).

### 2. `ExponentialBackoff` (Espera Exponencial)
*   Si falla el intento 1, espera 1s.
*   Si falla el intento 2, espera 2s.
*   Si falla el intento 3, espera 4s.
*   **Jitter**: Agrega un +/- 25% aleatorio para evitar que todos los hilos reintenten al mismo tiempo exacto (Thundering Herd).

### 3. `ErrorClassifier` (Clasificador de Errores)
No todos los errores merecen retry.
*   **Transient (Reintentar)**: `TimeoutException`, `StaleElementReference`. Son temporales.
*   **Permanent (Abortar)**: `ValueError`, `FileNotFound`. Reintentar no arreglará un archivo que no existe.

## 🛠️ Decorador `@retry`
Permite blindar cualquier función crítica con una sola línea:
```python
@retry(max_attempts=3, backoff=ExponentialBackoff())
def click_boton_ingresar():
    ...
```

## ⚠️ Importancia Crítica
Sin este módulo, el script sería extremadamente frágil. Sigges es una web inestable; este módulo es el amortiguador que absorbe esa inestabilidad.
