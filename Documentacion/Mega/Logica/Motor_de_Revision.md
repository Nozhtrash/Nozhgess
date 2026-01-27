# Motor de Conexiones (`Utilidades/Conexiones.py`)

## 📌 Propósito y Definición
Este es el **Cerebro (Master Orchestrator)**. No interactúa con el navegador (eso es `Driver.py`), sino que decide *qué hacer* con la información.
Siga el ciclo: Leer Excel -> Buscar -> Analizar Prestaciones -> Decidir si es Habilitante/Excluyente -> Escribir Resultado.

## ⚙️ Lógica de Negocio y Algoritmos

### 1. Selección de Caso Inteligente (`seleccionar_caso_inteligente`)
Cuando un paciente tiene múltiples casos abiertos (ej: Depresión leve, grave), ¿Cuál revisamos?
Se usa un algoritmo de **Puntuación Ponderada**:
*   **Filtro de Keywords**: Primero filtra casos que coincidan con palabras clave (configurado en misión).
*   **Puntaje**:
    *   Caso Activo: +10,000,000,000 puntos.
    *   Caso Cerrado: +0 puntos.
    *   Desempate: Timestamp de apertura (más reciente gana).
*   **Resultado**: Siempre prioriza el caso activo más nuevo que coincida con la patología.

### 2. Detección de Habilitantes (`listar_habilitantes`)
Revisa la lista de prestaciones buscando códigos específicos (ej: consultas médicas previas).
*   **Vigencia**: Calcula si la prestación ocurrió dentro de `VENTANA_VIGENCIA_DIAS` (Configurable) respecto a la fecha del caso.
    *   *Fórmula*: `Fecha_Prestación >= (Fecha_Caso - Ventana)` y `Fecha_Prestación <= Fecha_Caso`.

### 3. Inteligencia de Historia (Apto SE / RE)
Determina si un caso merece seguimiento ("Apto SE") o resolución ("Apto RE") mediante heurística de texto:
*   **Apto SE**: Busca la palabra "seguimiento" en:
    *   Estado actual del caso.
    *   Diagnósticos de IPD/OA/SIC.
    *   Derivaciones.
*   **Apto RE**: Se marca SI si:
    *   Existe un IPD con estado "Sí" (Confirmación diagnóstica).
    *   O existe un registro en APS (Atención Primaria).

### 4. Sistema de Reintentos Críticos (`procesar_paciente`)
Contiene un bucle `while intento < MAX` por paciente.
*   Si falla la lectura, **resetea el estado**:
    *   Intento 2: Va al Home y vuelve a buscar.
    *   Intento 3: Refresca la página y vuelve a buscar.
    *   Intento 4: Se rinde y marca "Error".

## 🛡️ Filosofía de Robustez (Heredado de v1.0.1)
El motor implementa patrones "Enterprise" documentados en `ESTADO_FINAL.md`:
1.  **Circuit Breaker**: Si fallan demasiados pacientes seguidos, el sistema podría detenerse (aunque actualmente está configurado para intentar sobrevivir 'Graceful Degradation').
2.  **Exponential Backoff**: Los tiempos de espera entre reintentos no son lineales. Aumentan (1s -> 2s -> 4s) para dar tiempo a que SIGGES se recupere.
3.  **Self-Healing**: Capacidad de detectar si el navegador murió y revivir la sesión (aunque depende de `Driver.py`).

## ⚠️ Debilidades y Puntos de Falla (Honestidad Brutal)
1.  **Cuello de Botella Secuencial**: Procesa paciente por paciente. Es lento (aprox 10-15s por paciente). No tiene paralelismo.
2.  **Fragilidad ante "Sin Caso"**: Si la mini-tabla no carga o está vacía, a veces el script asume erróneamente que no hay caso, cuando podría ser un error de carga de SIGGES. (Se ha mitigado con esperas, pero el riesgo persiste).
3.  **Complejidad Ciclómatica**: La función `analizar_mision` es enorme. Mezcla lógica de lectura, parseo, decisión y formateo. Es difícil de mantaner y propensa a bugs si se toca algo sin cuidado.

## 🔍 Detalles Técnicos
*   **Timing**: Usa `TimingContext` para medir cuánto tarda cada paso y generar logs de rendimiento.
*   **Excepciones**: Todo está envuelto en try-except masivos por paciente. Si falla un paciente, el script *intentará* seguir con el siguiente, pero una falla catastrófica en `Driver` podría detener todo el lote.
