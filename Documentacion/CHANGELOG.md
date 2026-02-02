# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
