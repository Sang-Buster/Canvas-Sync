<div align="center">
   <a href="https://github.com/Sang-Buster/Canvas-Sync">
      <img src="https://raw.githubusercontent.com/Sang-Buster/Canvas-Sync/refs/heads/main/docs/images/logo.png" width=30% alt="logo">
   </a>
   <h1>Canvas-Sync</h1>
   <a href="https://deepwiki.com/Sang-Buster/Canvas-Sync"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
   <a href="https://pypi.org/project/Canvas-Sync/"><img src="https://img.shields.io/pypi/v/Canvas-Sync" alt="PyPI"></a>
   <a href="https://github.com/Sang-Buster/Canvas-Sync/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Sang-Buster/Canvas-Sync" alt="License"></a>
   <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
   <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
   <a href="https://github.com/Sang-Buster/Canvas-Sync/commits/main"><img src="https://img.shields.io/github/last-commit/Sang-Buster/Canvas-Sync" alt="Last Commit"></a>
   <h6><small>Synchronize Canvas LMS courses and files to a local folder, preserving course structure and organization.</small></h6>
   <p><b>#Canvas &emsp; #Instructure &emsp; #LMS &emsp; #Synchronize &emsp; #Education</b></p>

</div>


## Table of Contents 📚
- [Overview](#overview)
- [Key Features](#key-features-)
- [Quick Start](#quick-start-)
- [Installation](#installation-)
- [Usage](#usage-️)
- [Configuration](#configuration-⚙️)
- [Security & Privacy](#security--privacy-🔒)
- [Development](#development-🛠️)
- [Links](#links-🔗)
- [Changelog](#changelog)

---

<h2 align="center">Overview</h2>

Canvas-Sync mirrors your Canvas course structure locally so you can browse course materials offline. It downloads modules, assignments, pages, files, and optional external resources into a tidy folder layout.

<h2 align="center">Key Features ⭐</h2>

<p align="center"><img src="docs/images/overview.png" alt="Overview" /></p>

- Automatic synchronization of modules, assignments, and files
- Preserves course/module/subfolder structure locally
- Configurable: choose which content types to sync
- Optional download of external files referenced in descriptions
- Simple, user-friendly CLI with interactive setup (Typer + Rich)

<h2 align="center">Quick Start 🚀</h2>

Follow these steps to get up and running quickly.

1) Generate a Canvas API token

   - Log in to your Canvas instance → **Account** → **Settings** → **Approved Integrations** → **New Access Token**.
   - Copy the token and keep it secure. You will use it during setup.

   <p align="center"><img src="https://raw.githubusercontent.com/Sang-Buster/Canvas-Sync/refs/heads/main/docs/images/auth_token.png" alt="Auth Token" /></p>

2) Install Canvas-Sync (pick one)

    Using `uv` (recommended):
    ```bash
    uv add canvas-sync
    uv pip install canvas-sync
    ```
    With `pip`:
    ```bash
    pip install canvas-sync
    ```
    From source (developer mode):
    ```bash
    git clone https://github.com/Sang-Buster/Canvas-Sync.git
    cd Canvas-Sync
    pip install -e .
    PYTHONPATH=src canvas --help
    ```

3) Launch and configure

   - Run `canvas` to launch the interactive setup. Choose choose a local sync folder, provide your Canvas domain, the API token from step 1, and select courses to be synced.
   - After setup, run `canvas sync` to begin downloading course content.

4) Usage, Configuration, and Common Flags

    - `canvas --help` — Launch CLI and show help message
    - `canvas setup` — Re-run setup and update saved values
    - `canvas info` — Show current saved settings
    - `canvas sync` — Start synchronization using saved settings
    - `canvas reset` — Reset and remove saved encrypted settings (use when you forgot your password)

    Configuration notes:
    - Settings are stored encrypted locally. Use `canvas --setup` to change them or `canvas reset` to remove them.

<h2 align="center">Security & Privacy 🔒</h2>

- Your Canvas API token is encrypted locally using AES and a password-derived key.
- Canvas-Sync is read-only: it only downloads course content and does not modify Canvas.
- Do not share your token; if compromised, revoke it in Canvas and run `canvas reset`.

<h2 align="center">Links 🔗</h2>

- Architecture notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Releases and changelog: [CHANGELOG.md](CHANGELOG.md)
