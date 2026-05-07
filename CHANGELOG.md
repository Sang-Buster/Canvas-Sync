
# CHANGELOG

All notable changes to this project are documented in this file.

## [0.5.0] - 2026-05-07
### Added
- Improvements to readme and documentation to reflect the latest features and usage patterns.
- Added more detailed architecture notes to help new contributors understand the codebase structure and design decisions.

## [0.4.0] - 2026-05-07
### Fixed
- Progress bar now only shows courses that are actually being synced (skipped courses no longer appear)
- Eliminated duplicate DOWNLOADING/SYNCED lines — each file now prints exactly one final status line
- Replaced broken `str(self)` slice approach in `print_status` with a proper `_print_leaf` helper

### Changed
- All entity `__repr__` methods now use clean indent-based Rich markup instead of legacy tab/space alignment
- Leaf items use icon-based status output: `↓` downloaded, `✓` already present, `✗` locked/failed, `⌁` URL shortcut
- Container entities use colored `■` bullets; courses use `▶` (syncing) and `▷` (skipped)

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