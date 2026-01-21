# Nozhgess v3.0 LEGENDARY - Manual de Referencia

<div align="center">

**⚕️ Automatización Inteligente de Datos Médicos**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.0.0-purple.svg)]()

</div>

---

## 📋 Descripción General

**Nozhgess** es una plataforma de automatización diseñada para optimizar la interacción con el sistema SIGGES. Esta versión v3.0 introduce una arquitectura más limpia y organizada, separando el núcleo de la aplicación de la configuración del usuario y la documentación.

### ✨ Características Destacadas
- **Arquitectura Segura**: Separación clara entre código (`App/`), configuración del usuario y documentación.
- **Doble Modo**: Funciona perfectamente desde la Interfaz Gráfica (GUI) o directamente desde un entorno de desarrollo (IDE).
- **Resiliencia Extrema**: Sistema de detección de fallos, circuit breakers y validación de contratos en tiempo real.
- **Portabilidad**: Preparado para ser compilado como un ejecutable independiente.

---

## 📁 Nueva Estructura Organizada

El proyecto se divide estratégicamente para facilitar su mantenimiento:

### 🏠 Carpeta Raíz (Espacio de Trabajo)
- 📂 **[App](file:///App)**: Contiene el "cerebro" y el código fuente.
- 📂 **[Documentacion](file:///Documentacion)**: Manuales, licencias y registros.
- 📂 **[Lista de Misiones](file:///Lista%20de%20Misiones)**: Definiciones de tareas de automatización.
- 📂 **[Mision_Actual](file:///Mision_Actual)**: Estado y configuración de la tarea en curso.
- 📂 **[Logs](file:///Logs)**: Registros detallados de cada ejecución.
- 📂 **[Utilidades](file:///Utilidades)**, **[Iniciador](file:///Iniciador)**: Herramientas complementarias.

---

## 🚀 Guías de Inicio

### Para Usuarios Finales
1. **Instalación**: Ejecuta [INSTALAR.bat](file:///INSTALAR.bat) para crear un acceso directo en tu escritorio.
2. **Inicio**: Usa [INICIAR_NOZHGESS.bat](file:///INICIAR_NOZHGESS.bat) para abrir la aplicación.
3. **Configuración**: La aplicación creará automáticamente las carpetas necesarias en el primer inicio.

### Para Desarrolladores (IDE)
1. Instala dependencias: `pip install -r App/requirements.txt`.
2. Punto de entrada: [App/Nozhgess.pyw](file:///App/Nozhgess.pyw).
3. Añade la raíz del proyecto a tu `PYTHONPATH` para que los módulos encuentren las carpetas de misiones.

---

## 📄 Licencia y Copyright
Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](file:///Documentacion/LICENSE) para más detalles.

© 2026 Nozhgess Team. Desarrollado para la eficiencia en salud.
