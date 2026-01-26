# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-01-26

### 🚀 Major Improvements
- **Terminal UI ("General" Tab) Fix**: Rewrote the log routing logic in `runner.py`. Previously, an aggressive filter prevented most real-time logs from appearing in the "General" tab, showing only separators. Now, it correctly mirrors the full log system, providing real-time visibility into the script's decision-making process.
- **Documentation Overhaul**: Added `DEVELOPMENT.md` (Architecture) and `TROUBLESHOOTING.md` (Diagnostics). Completely rewrote `README.md` to serve as a professional project hub.

### 🐛 Bug Fixes
- **Infinite Navigation Loop**: Fixed a critical recursion bug in `Driver.py` (`asegurar_en_busqueda`). The fallback mechanism called `self.ir()`, which internally intercepted the URL and called `asegurar_en_busqueda` again. Replaced with `self.driver.get()` direct navigation.
- **Configuration Auto-Healing**: Addressed a JSON corruption issue where lists were saved as strings (e.g., `"['Item']"` instead of `["Item"]`). The `MisionController` now detects and automatically repairs malformed lists upon loading or saving.
- **Import Path Resolution**: Resolved `ImportError` caused by renaming the `Mision_Actual` folder. Updated `Conexiones.py` and strictly verified all `from Mision_Actual import ...` statements.
- **Spinner Detection**: Enhanced `SPINNER_CSS` in `Direcciones.py` to include `dialog.loading[open]`, significantly improving the script's ability to "wait" for modern web overlays.

### 🔧 Technical Refactoring
- **Log Routing Logic**: Modified `StreamRedirector` in `runner.py` to classify "Trace" (✓, ⏳) and "Summary" (🔥) logs correctly into the General stream, repairing the broken UI experience.
- **Wait Strategies**: Tuned `_wait_smart` in `Driver.py` to have a slightly longer grace period (150ms), reducing false positives when checking for spinners on laggy networks.

## [3.0.0] - 2026-01-26 (Initial Major Release)

### Added
- **Real-time Control Panel**: Missions now update immediately in the GUI when created, deleted, or modified.
- **Universal Compatibility**: Enhanced `universal_compatibility.py` to support new project structure.
- **Improved Logging**: Better error handling and visibility in `Terminal.py` and `runner.py`.

### Changed
- **Project Structure Overhaul**:
    - Renamed folder `Mision_Actual` to `Mision Actual` (Cleaner naming).
    - Merged `A_Lista de Misiones` into `Lista de Misiones`.
    - Merged `Z_Utilidades` into `Utilidades`.
    - Removed redundant `C_Mision` folder.
- **Path Handling**:
    - Updated `sys.path` injection in `app.py` and `bootstrap.py`.
    - Updated all import statements to reflect the new structure.

### Removed
- **Duplicate Directories**: Cleaned up `A_`, `Z_` and `C_` prefixed folders.
