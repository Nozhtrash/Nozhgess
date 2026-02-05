# 📘 GUIA OPERATIVA MAESTRA NOZHGESS v3.4.0
> **Perfil:** Operadores Administrativos, Gestores GES y Auditores Clínicos.
> **Versión:** 3.4.0 "Forensic Edition"

---

# 1. EL FLUJO DE TRABAJO PERFECTO

Para garantizar que el robot no cometa errores, siga este ritual de inicio:

1.  **Limpieza:** Cierre todas las ventanas de Edge.
2.  **Ignición:** Abra `Nozhgess.pyw`.
3.  **Conexión Debug:** Presione "Iniciar Edge (Debug)". Se abrirá una ventana de Edge especial.
4.  **Login Humano:** Inicie sesión en SIGGES manualmente en esa ventana.
5.  **Posicionamiento:** Quédese en la pantalla principal de SIGGES (donde se selecciona el establecimiento).

---

# 2. EL NUEVO BUSCADOR DE LOGS (INTELIGENTE)

Hemos optimizado la consola negra (Terminal) para que sea su mejor herramienta de auditoría.

### Cómo buscar un paciente o error:
1.  **Escribir:** Ponga el RUT o el texto en el campo de búsqueda (arriba a la derecha).
2.  **Disparar:** Presione la tecla **ENTER** o el botón **Buscar**. 
3.  **Navegar:** Use las flechas o presione Enter repetidamente para saltar entre coincidencias.
4.  **Resaltado:** 
    *   **Amarillo:** Todas las veces que aparece el término.
    *   **Naranja:** La coincidencia en la que está parado actualmente.

> [!TIP]
> Si el robot se detiene, busque la palabra "Error" o "FALLO" para ver exactamente en qué paso se quedó.

---

# 3. INTERPRETANDO EL REPORTE EXCEL (AVANZADO)

El Excel generado por Nozhgess v3.4.0 es ahora más inteligente.

### 🔴 Alertas de Caso en Contra
Si su misión detecta un caso que no corresponde (ej. busca un T2 y hay un T1 activo), verá:
- **Columna "Caso en Contra":** Nombre del caso divergente encontrado.
- **Columna "Apto Caso":** Un diagnóstico automático (ej. "IPD + Reciente"). Si dice esto, es muy probable que el paciente esté mal ingresado en la nómina.

### 🟣 Frecuencias y Periodicidad
- **Freq CodxAño:** Le dirá de forma resumida si el paciente cumple con su control anual/mensual.
- **Vigente / No Vigente:** Cálculo automático basado en la fecha de la nómina vs la fecha del último examen encontrado.

---

# 4. TABLA DE RESOLUCIÓN DE PROBLEMAS (SOPORTE)

| Problema | Causa Probable | Solución Inmediata |
| :--- | :--- | :--- |
| **"Buscando RUT..." eterno** | SIGGES no responde o la sesión expiró. | Refresque la página de Edge manualmente. |
| **Buscador de Logs lento** | Hay más de 1000 coincidencias. | Sea más específico en su búsqueda (ej. use el RUT completo). |
| **Excel bloqueado** | Intentó generar el reporte con el Excel viejo abierto. | Cierre Excel y vuelva a presionar "Ejecutar" para los pacientes restantes. |
| **Botón 'Ejecutar' gris** | No se ha cargado el archivo de entrada. | Arrastre su archivo Excel al área designada. |

---

# 5. CONSEJOS DE SEGURIDAD CLÍNICA
- **Auditores:** Nozhgess es un filtro. Siempre revise manualmente los casos marcados en **ROJO** (Habilitantes) antes de firmar un egreso.
- **IT/Soporte:** No mueva los archivos de la carpeta `Utilidades` ni `App/config` sin una copia de seguridad.

---
**© 2026 Nozhgess Support Team**
*"La precisión es nuestra única garantía."*
