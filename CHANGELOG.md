
# CHANGELOG

All notable changes to this project are documented in this file.

## [0.3.0] - 2026-05-07
### Added
- Rich progress bars for `canvas sync` with per-course task tracking
- Rich table rendering for `canvas info` and settings displays
- Shared Rich console utility for consistent CLI output across modules

### Changed
- Replaced legacy ANSI-based sync output in entities with Rich-styled status lines
- Updated interactive setup prompts to use Rich prompts (while preserving checkbox course selection with questionary)
- Removed sync-time console clearing in `Synchronizer` to preserve CLI header/progress visibility
- Updated README and architecture docs to reflect the new CLI UX and rendering flow

## [0.2.0] - 2026-05-07
- Renamed package to `canvas-sync-py` for PyPI distribution
- Updated README and documentation to reflect new package name
- Refactored file path construction to use `os.path.join()` for better cross-platform compatibility

## [0.1.0] - 2026-05-07
### Added
- Initial release with core synchronization features
- Support for modules, assignments, files, and external links
- Configurable sync options and secure credential storage
- Basic error handling and logging
- Command-line interface (Typer + Rich)
- Documentation and architecture notes