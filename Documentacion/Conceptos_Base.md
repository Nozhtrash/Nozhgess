# 🏥 Transparencia y Conceptos Base

Este documento detalla la lógica interna de Nozhgess y cómo interactúa con los sistemas de salud. La transparencia es vital para garantizar la confianza en los resultados de la automatización.

---

## 🔍 ¿Cómo funciona Nozhgess?

Nozhgess utiliza **automatización robótica de procesos (RPA)** mediante Selenium para simular las acciones de un operador humano en el sistema SIGGES. 

### El Flujo de Trabajo
1.  **Orquestación**: Lee una lista de misiones (archivos Excel o configuraciones en Python).
2.  **Preparación**: Inyecta parámetros de búsqueda y filtros en el motor de automatización.
3.  **Ejecución**: Navega por las páginas de SIGGES, detecta elementos dinámicos y extrae o ingresa información según la misión.
4.  **Validación**: Cada dato extraído pasa por un motor de validación local antes de ser registrado en los reportes de salida.

---

## ⚖️ Reglas de Negocio y Lógica Clínica

Nozhgess no toma decisiones arbitrarias. Su comportamiento se basa en reglas estrictas:

### 1. Validación de Identidad (RUT)
*   Aplica el algoritmo del dígito verificador para asegurar que cada RUT procesado es válido.
*   Ignora automáticamente registros con formatos corruptos para evitar contaminar la base de datos de salida.

### 2. Filtros de Categorización
La app utiliza códigos específicos para clasificar a los pacientes:
*   **IPD**: Información al Paciente (Garantías).
*   **OA**: Orden de Atención.
*   **APS**: Atención Primaria de Salud.
*   **SIC**: Sistema Interconectado.

### 3. Sistema de Priorización
Si un paciente tiene múltiples casos, Nozhgess utiliza una lógica de "Puntaje de Confianza" para decidir cuál es el caso más relevante basado en la fecha de apertura y el estado del proceso.

---

## 🛡️ Ética y Privacidad de Datos

*   **Procesamiento Local**: Nozhgess no envía datos a servidores externos. Toda la información de los pacientes permanece dentro de la red local del usuario.
*   **Auditabilidad**: Cada clic y cada decisión tomada por el robot queda registrada en los archivos de la carpeta `Logs/`.
*   **Cumplimiento**: La herramienta está diseñada para asistir al profesional en tareas repetitivas, permitiendo siempre la intervención humana.

---
© 2026 Nozhgess Team.
