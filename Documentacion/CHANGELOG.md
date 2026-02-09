# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.1] - 2026-02-08
### 🧹 Infraestructura y Documentación Forense
- **Limpieza Masiva de Residuos:** Eliminación de archivos `.bak`, logs temporales y dependencias huérfanas identificadas en la auditoría.
- **Rediseño del README:** Migración total a español y actualización de capacidades técnicas (Session Parasitism v2 e Intergrator).
- **Actualización Maestra de Documentación:** Sincronización de todas las guías técnicas con la arquitectura actual del sistema.
- **Mejora del Diccionario de Errores:** Clasificación forense expandida con protocolos de resolución nivel 3.

## [3.4.0] - 2026-02-05

### 🛡️ Forensic Logic & Robustness
- **"Caso en Contra" Full Fix:** Resolved a critical bug where the "En Contra" block was ignored due to missing column initialization.
- **Auto-Initialization:** The results dictionary now pre-fills all columns from the mission config, preventing silent failures and guaranteeing Excel consistency.
- **Smart Selection Upgrade:** Improved keywords matching and "Active Case" prioritization in `seleccionar_caso_inteligente`.

### 🔍 Search & Performance
- **Optimized Log Search:** Replaced real-time searching with an explicit trigger (Enter/Button) to eliminate application lag and crashes.
- **Dual Highlighting:** Implemented a new tagging system in the console (Yellow for all matches, Orange for the current focus).
- **Match Navigation:** Added a limit of 1000 highlights to ensure UI responsiveness.

### 📚 Documentation (The "Great Expansion")
- **Manual Overhaul:** Rewrote all specialized manuals to reflect v3.4.0 capabilities.
- **New Guides:** Added `GUIA_CONFIGURACION_MISIONES.md` (JSON reference) and `ESTANDAR_DE_CODIGO.md` (Maintenance philosophy).

## [3.3.0] - 2026-02-04
### 🛡️ Audit & Compliance (Critical)
- **Strict Limit Enforcement:** Fixed a core logic flaw where global defaults overrode mission limits. `Analisis_Misiones.py` now strictly obeys `max_habilitantes`, `max_objetivos`, etc., from `mission_config.json`.
- **Ghost Column Elimination:** Implemented strict conditional logic in `Conexiones.py`. Columns like "Código Año", "Apto Caso", "Folio VIH", and "Observación Folio" now ONLY appear if explicitly enabled in the mission.

### 📊 Excel Reporting Engine 3.0
- **Dynamic "Diccionario" Sheet:** Now features categorized columns ("Identificación", "Clínico", "Lógica"), detailed technical descriptions, and premium dark-blue styling. Auto-generated in every report.
- **New "Carga Masiva" Sheet:** Automatically generates a specific sheet for bulk uploads (Cyan headers) with columns: `Fecha`, `Rut`, `DV`, `Prestaciones`, `Tipo`, `PS-Fam`, `Especialidad`. (Data population pending/manual as requested).

### 🐛 Bug Fixes
- **Folio VIH Consistency:** Fixed a discrepancy where column creation used a global default (True) but data filling used a local default (False). Now forced to `False` (Opt-in) everywhere.

## [3.2.0] - 2026-02-02
### 🚀 Critical Improvements
- **Nuclea Login Fix:** Implemented a robust "Visual + Native Event" strategy for the login process (`flows.py`). 
    - Added red/yellow visual highlighting for detected buttons.
    - Replaced standard Selenium clicks with JavaScript Event Dispatch (`mousedown` -> `mouseup` -> `click`) to bypass UI lag.
    - Applied mainly to the "Ingresar" button, with standard fallbacks for subsequent steps.

### 🎨 UI/UX & Reporting
- **Excel Styles V2:** Complete overhaul of `Excel_Revision.py`.
    - Introduced a Strict Color Palette: Blue (Identity), Green (Status), Coffee (Time), Purple (Contra), Pink (Aptos).
    - Restored the "Periodicidad" column next to "Mensual" in `Conexiones.py`.
    - Enforced White/Bold text for high-contrast readability.

### 📚 Documentation
- **Consolidation:** Merged 10+ scattered documentation files into two master documents:
    - `MANUAL_USUARIO.md`: Installation + Operations + Troubleshooting.
    - `MANUAL_TECNICO.md`: Architecture + Logs + Development Logic.
- **Cleanup:** Removed obsolete architecture diagrams and temporary logs.

---

## [3.1.2] - 2026-01-28
### 🧹 Global Audit & Cleanup
- **Deep Codebase Cleanup**: Deleted over 10 experimental and unused files (`enhanced_app.py`, `intelligent_preloader.py`, etc) to reduce technical debt and confusion.
- **Timing Consolidation**: Replaced legacy `Timing.py` with the robust `Timing2.py` mechanism.
- **Safety Hardening**: Added explicit "DO NOT EDIT" headers to `Mision_Actual.py`.

### 🚀 New Features
- **Control Panel Quick Search**: Added a real-time search bar to filter mission shortcuts, addressing user feedback about difficulty finding missions in long lists.

## [3.1.1] - 2026-01-28
### 🚀 Major Improvements
- **Mission Management 2.0 (Json Support)**: Transitioned mission storage to modern `.json` format while maintaining backward compatibility with legacy `.py` files.
- **Unified Saving UX**: Overhauled the Control Panel save dialog.

### 🐛 Bug Fixes
- **Invisible Saves**: Fixed a file filter bug in `missions.py`.
- **Loader Robustness**: Updated `_load_as_current` to self-heal.

## [3.1.0] - 2026-01-26
### 🚀 Major Improvements
- **Terminal UI ("General" Tab) Fix**: Rewrote the log routing logic in `runner.py`.
- **Documentation Overhaul**: Added initial drafts of Manuals.

### 🐛 Bug Fixes
- **Infinite Navigation Loop**: Fixed recursion in `Driver.py`.
- **Configuration Auto-Healing**: Addressed JSON corruption issues.
- **Spinner Detection**: Enhanced `SPINNER_CSS`.

## [3.0.0] - 2026-01-26 (Initial Major Release)
### Added
- **Real-time Control Panel**.
- **Universal Compatibility**.
- **Improved Logging**.

### Changed
- **Project Structure Overhaul**: Cleaning up `A_`, `Z_` and `C_` folders.
