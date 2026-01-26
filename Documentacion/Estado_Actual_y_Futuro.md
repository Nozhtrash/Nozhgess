# 🔮 Estado Actual y Futuro del Proyecto

## 🚦 Estado Actual (v1.2 - Enero 2026)
El sistema **Nozhgess** se encuentra en un estado funcional estable tras la corrección de los bugs críticos de "Sin Caso" y mezcla de terminales.

### ✅ Lo que funciona perfectamente:
*   **Navegación Robusta:** Sistema de reintentos y detección de spinners pulido.
*   **Logs y Observabilidad:** Trifecta de terminales (Principal, Debug, General) operando con roles definidos.
*   **Panel de Control:** Guardado seguro de misiones con sanitización de inputs para evitar corrupciones.
*   **Detección de Casos:** Lógica de keywords y scoring (vigencia/estado) validada.

### ⚠️ Lo que es frágil (Debilidades Conocidas):
1.  **Dependencia del Port 9222:** Si Edge se cierra o cambia de puerto, el robot no conecta.
    *   *Mitigación:* Usar siempre el script `Iniciador Web.ps1`.
2.  **Copy-Paste de Configuración:** Aunque sanitizamos, copiar texto con formato extraño desde Excel/Web podría introducir caracteres invisibles.
    *   *Consejo:* Escribir manualmente las keywords separadas por coma simple si hay duda.
3.  **Tiempos de Espera (Waits):** En PCs muy lentos, los `WebDriverWait` de 10s podrían quedarse cortos. Se pueden ajustar en `config.py`.

---

## 📅 Roadmap (Mejoras Futuras)

Para llevar el proyecto al siguiente nivel (v2.0), se sugieren estas evoluciones:

### 1. Base de Datos Real (SQLite/Postgres)
*   **Por qué:** Actualmente usamos `mission_config.json` y archivos de texto `.log`. Esto escala mal.
*   **Mejora:** Guardar historial de casos, resultados y config en una BD local `sqlite`. Permitiría sacar estadísticas ("¿Cuántos casos cerré este mes?").

### 2. Dashboard de Métricas
*   **Por qué:** Solo vemos texto.
*   **Mejora:** Una pestaña "Gráficos" en el Panel de Control con tortas de "Éxito vs Fallo" y "Tiempos Promedio".

### 3. "Auto-Healing" de Conexión
*   **Por qué:** Si se cae internet, el script falla.
*   **Mejora:** Detectar desconexión, pausar automáticamente ("⏳ Esperando red..."), y reanudar al volver.

---

## 🔙 Protocolo de Emergencia (Rollback)

Si una actualización rompe el sistema, sigue estos pasos para volver a un estado funcional seguro:

1.  **Restaurar Configuración:**
    *   Ve a `App/config/`.
    *   Borra `mission_config.json`.
    *   Renombra `mission_config.json.bak` (si existe) o copia uno de los backups automáticos si se implementaron.
    *   *Si no hay backup:* Crea uno nuevo desde el Panel de Control (botón `+`) con datos limpios.

2.  **Limpiar Logs:**
    *   Borra todo el contenido de `Logs/`. A veces un archivo corrupto bloquea el inicio.

3.  **Verificar Dependencias:**
    *   Ejecutar `pip install -r requirements.txt` por si alguna librería (como `colorama`) se desinstaló.

4.  **Validar Python:**
    *   Asegúrate de estar corriendo con el entorno virtual correcto (`.venv`) y no con el Python base de Windows.
