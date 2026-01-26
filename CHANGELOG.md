# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-01-26

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
    - Updated `sys.path` injection in `app.py` and `bootstrap.py` to support directory names with spaces.
    - Updated all import statements to reflect the new structure.
- **Button Logic**:
    - Audited and updated logic for "Usar Ahora", "Guardar", "Exportar" and other mission management buttons.
    - Fixed specific paths in `vba_viewer.py` and `backups_viewer.py`.

### Fixed
- Fixed `ImportError` issues caused by folder renaming.
- Resolved potential conflicts with `Mision_Actual` module importing.
- Ensured PyInstaller `nozhgess.spec` points to the correct directories.

### Removed
- **Duplicate Directories**: Cleaned up `A_`, `Z_` and `C_` prefixed folders to enforce a clean, professional structure.
