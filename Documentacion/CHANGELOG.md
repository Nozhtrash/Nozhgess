# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.0.0] - 2026-01-20

### ✨ Added (Agregado)

- **Sistema de Diseño Premium**
  - 20 colores de acento predefinidos
  - Sistema de gradientes (8 variantes)
  - Sistema de sombras (7 niveles)
  - Tokens de espaciado y border radius
  - Soporte para glassmorphism

- **Settings Completo**
  - Sección Apariencia (tema, colores, escala)
  - Sección Ventana (posición, tamaño, siempre visible)
  - Sección Notificaciones (sonidos, alertas Windows)
  - Sección Datos (limpieza logs, export/import config)
  - Sección Rendimiento (animaciones, modo ahorro)
  - Sección Atajos de Teclado
  - Sección Avanzado (debug, reset)

- **Dashboard Renovado**
  - Hero section con botón principal grande
  - Grid de estadísticas con hover effects
  - Quick actions mejorados
  - Activity feed con timeline
  - Estado del sistema en tiempo real

- **Componentes Premium**
  - `PremiumCard` con sombras y hover
  - `PremiumButton` con variantes
  - `GradientButton` para acciones principales
  - `StatCard` para estadísticas
  - `SectionHeader` para organización
  - `LoadingSpinner` animado
  - `InfoBadge` para estados

- **Sidebar Moderno**
  - Ancho aumentado a 100px
  - Iconos más grandes (20px)
  - Indicador activo con color de acento
  - Hover effects suaves
  - Secciones bien diferenciadas
  - Footer con año dinámico

- **Testing**
  - Directorio `tests/` con estructura
  - 28 tests para validaciones (RUT, fecha, nombre)
  - 25 tests para sistema de temas
  - Configuración pytest

- **Backend**
  - `constants.py` centralizado con todos los timeouts/URLs
  - Limpieza de archivos de backup

- **Documentación**
  - README.md profesional con badges
  - CHANGELOG.md con historial

### 🔄 Changed (Modificado)

- **theme.py**: Reescrito completamente con nuevo sistema de diseño
- **sidebar.py**: Rediseñado con layout moderno
- **dashboard.py**: Nueva estructura con componentes premium
- **settings.py**: Expandido de 2 a 25+ opciones
- **app.py**: Lazy loading de vistas, persistencia de ventana

### 🗑️ Removed (Eliminado)

- Archivos de backup `.pre_optimization_*` y `.pre_perfection_*`
- Código comentado obsoleto

---

## [1.0.0] - 2025-12-01

### Added

- Versión inicial de Nozhgess
- Interfaz GUI básica con CustomTkinter
- Motor de automatización con Selenium
- Sistema de reintentos con circuit breaker
- Validación de RUT chileno
- Generación de Excel de resultados
- Sistema de logging con rotación
