# 🔥 Nozhgess v1.0

> **Automatización inteligente de revisión de datos médicos en SIGGES**  
> Sistema profesional de procesamiento automatizado con GUI moderna y logging avanzado

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Made with ♥](https://img.shields.io/badge/Made%20with-♥-red.svg)](https://github.com/Nozhtrash)

---

## ✨ Características Principales

- 🚀 **Procesamiento Automatizado** - Revisa pacientes en SIGGES automáticamente
- 📊 **Sistema de Logs Dual** - Terminal (resúmenes) y Debug (detalles técnicos)
- ⏸️ **Controles de Ejecución** - Pause, Resume y Stop durante el procesamiento
- 🎨 **GUI Moderna** - Interfaz construida con CustomTkinter
- 🛡️ **Crash Reporting** - Sistema de reportes automáticos de errores
- 🌐 **Edge Integration** - Control inteligente del navegador en modo debug
- 📈 **Progress Tracking** - Barra de progreso con ETA calculation

---

## 📋 Requisitos

### Software Necesario
- **Python 3.8+**
- **Microsoft Edge** (con WebDriver)
- **Windows 10/11**

### Dependencias Python
```bash
customtkinter>=5.2.0
selenium>=4.0.0
pandas
openpyxl
webdriver_manager
psutil
colorama
win10toast
```

---

## 🚀 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Nozhtrash/Nozhgess.git
cd Nozhgess
```

### 2. Crear Entorno Virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Misión
Edita `Mision_Actual/Mision_Actual.py` con tu configuración:
```python
NOMBRE_DE_LA_MISION = "Tu Misión"
ARCHIVO_PACIENTES = "tu_archivo.xlsx"
# ... más configuraciones
```

---

## 💻 Uso

### Opción 1: Interfaz Gráfica (GUI)
```bash
python Nozhgess.pyw
```

1. Click en "Iniciar Edge Debug"
2. Click en "Abrir SIGGES"
3. Presiona "▶ Iniciar"
4. Monitorea el progreso en tiempo real

### Opción 2: Línea de Comandos
```bash
python "Iniciador/Iniciador Script.py"
```

**Ventajas:**
- ✅ Logs completos en terminal
- ✅ Mejor control y debugging
- ✅ Más estable

---

## 📁 Estructura del Proyecto

```
Nozhgess/
├── Nozhgess.pyw           # Entry point GUI
├── requirements.txt        # Dependencias
├── .gitignore             # Exclusiones Git
│
├── Mision_Actual/         # Configuración de misiones
│   └── Mision_Actual.py   # Parámetros principales
│
├── Iniciador/             # Scripts de inicio
│   ├── Iniciador Script.py
│   └── Iniciador Web.ps1
│
├── Utilidades/            # Core del sistema
│   ├── GUI/               # Interfaz gráfica
│   │   ├── app.py
│   │   ├── theme.py
│   │   └── views/
│   ├── Motor/             # WebDriver manager
│   ├── Mezclador/         # Lógica principal
│   ├── Principales/       # Utilidades core
│   └── ...
│
├── Extras/                # Herramientas adicionales
│   └── VBA/               # Macros Excel
│
├── Entrada/               # Excel de pacientes (gitignored)
├── Salida/                # Resultados (gitignored)
└── Logs/                  # Logs de ejecución (gitignored)
```

---

## 🎯 Funcionalidades Avanzadas

### Sistema de Logs Separados
- **Terminal**: Resúmenes limpios con emojis
- **Debug**: Detalles técnicos completos

### Control de Ejecución
- **Pause** (Espacio): Pausa el procesamiento
- **Resume**: Continúa desde donde pausó
- **Stop** (Esc): Detiene limpiamente

### Smart Browser Management
- Solo cierra sesiones debug (puerto 9222)
- No interfiere con navegación normal

---

## ⚙️ Configuración Avanzada

### Parámetros en `Mision_Actual.py`

```python
# Navegador
DIRECCION_DEBUG_EDGE = "localhost:9222"
EDGE_DRIVER_PATH = ""  # Vacío = auto-descarga

# Timeouts
TIEMPO_TIMEOUT_SPINNER = 0.5
TIEMPO_BASE_ESPERA_CARGA = 8

# Excel
HOJA_PARA_USAR = "Hoja1"
COLUMNA_RUT = "A"
```

---

## 🐛 Troubleshooting

### Script no inicia
```bash
# Verificar Edge debug está corriendo
curl http://localhost:9222/json
```

### WebDriver error
- Dejar `EDGE_DRIVER_PATH = ""` para auto-gestión
- Selenium Manager descargará la versión correcta

### Logs no aparecen
- Usar script desde terminal para mejor debugging
- Revisar carpeta `Logs/`

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Para cambios importantes:

1. Fork el proyecto
2. Crea tu Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al Branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👤 Autor

**Nozhtrash**

- GitHub: [@Nozhtrash](https://github.com/Nozhtrash)
- Proyecto: [Nozhgess](https://github.com/Nozhtrash/Nozhgess)

---

## 🙏 Agradecimientos

- CustomTkinter por la GUI moderna
- Selenium por la automatización web
- Comunidad Python por las herramientas

---

<div align="center">

**Made with ♥ by Nozhtrash © 2026**

⭐ Si este proyecto te ayuda, dale una estrella!

</div>
