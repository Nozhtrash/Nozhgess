# Driver y Navegador (`Utilidades/Driver.py`)

## 📌 Propósito y Definición
Este módulo es el **Wrapper de Selenium**, la capa que interactúa físicamente con el navegador Edge. Es una abstracción de alto nivel diseñada para ser **"NASA Luxury"**, priorizando la estabilidad sobre la velocidad bruta.

## ⚙️ Lógica y Mecánicas

### 1. Conexión Debug (Puerto 9222)
A diferencia de scripts tradicionales que abren una ventana nueva, este Driver se **conecta** a una ventana existente.
*   **Ventaja**: Permite al usuario loguearse manualmente, resolver CAPTCHAs y mantener la sesión.
*   **Lógica**: `options.debugger_address = "localhost:9222"`.

### 2. Esperas Inteligentes (`_wait_smart`)
No usa `time.sleep()` fijos. Implementa una lógica híbrida:
1.  **Detección Instantánea**: Verifica si existe un spinner de carga (`dialog.loading` o similar). Si NO existe, retorna en ~1ms.
2.  **Timeout Dinámico**: Si el spinner existe, espera hasta que desaparezca con un timeout de 1.5s (optimizado en v2.0).
3.  **Efecto**: Si la página vuela, el script vuela. Si la página se arrastra, el script espera.

### 3. Máquina de Estados (`detectar_estado_actual`)
Para no perderse en la navegación, el Driver intenta "adivinar" dónde está mirando:
*   **Algoritmo**:
    1.  Verifica URL estable (polling 300ms).
    2.  Busca elementos ancla (botón "Ingresar" = LOGIN, input RUT = BUSQUEDA).
    3.  **Caché**: Guarda el estado por 2 segundos para no machacar el DOM con consultas repetitivas.

### 4. Navegación Robusta (`buscar_paciente`, `ir_a_cartola`)
Implementa "Retry Patterns". Si falla un click o una búsqueda:
1.  Captura la excepción.
2.  Espera un tiempo exponencial (`reintento_1`, `reintento_2`).
3.  Intenta corregir el estado (ej: re-abrir menú lateral).
4.  Reintenta la acción.

## 🧮 Matemáticas Ocultas
*   **Exponential Backoff**: Aunque simple, los tiempos de espera aumentan (1s -> 2s -> 5s) en los reintentos definidos en `Conexiones.py`, aunque la lógica base está en el driver.

## ⚠️ Debilidades y Puntos de Falla (Honestidad Brutal)
1.  **El "Drift" de Selectores**: Todo el Driver depende de `XPATHS` (importado de `Direcciones.py` - **Falta documentar**). Si SIGGES cambia el ID de un botón mañana, el script muere instantáneamente. Es extremadamente frágil a cambios en el Frontend de SIGGES.
2.  **Dependencia de `focus`**: Selenium a veces requiere que la ventana tenga foco para ciertos eventos JS. Si el usuario minimiza la ventana o la tapa, *podría* haber timeouts extraños (aunque funciona en background la mayoría de veces).
3.  **Puerto Zombi**: Si Edge se cierra mal y deja el proceso colgado manteniendo el puerto 9222 ocupado, el script no podrá conectarse o conectará a una ventana fantasma.

## 🐛 Historial de Bugs Relevantes
*   **"Spinner Stuck"**: Hubo un tiempo donde el script esperaba 30 segundos por un spinner invisible. Se arregló con `_wait_smart` que verifica visibilidad real.
*   **Timeout esperando elemento**: Clásico. Se mitiga con los reintentos, pero sigue siendo la causa #1 de fallos en redes lentas.
