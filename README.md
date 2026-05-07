<div align="center">
  <a href="https://github.com/Sang-Buster/Canvas-Sync">
     <img src="https://raw.githubusercontent.com/Sang-Buster/Canvas-Sync/refs/heads/main/docs/images/logo.png" width=30% alt="logo">
  </a>
  <h1>Canvas-Sync</h1>
  <a href="https://deepwiki.com/Sang-Buster/Canvas-Sync"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
  <a href="https://pypi.org/project/Canvas-Sync/"><img src="https://img.shields.io/pypi/v/canvas-sync-py" alt="PyPI"></a>
  <a href="https://github.com/Sang-Buster/Canvas-Sync/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Sang-Buster/Canvas-Sync" alt="License"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/Sang-Buster/Canvas-Sync/commits/main"><img src="https://img.shields.io/github/last-commit/Sang-Buster/Canvas-Sync" alt="Last Commit"></a>
  <h6><small>Synchronize Canvas LMS courses and files to a local folder, preserving course structure and organization.</small></h6>
  <p><b>#Canvas &emsp; #Instructure &emsp; #LMS &emsp; #Synchronize &emsp; #Education</b></p>
</div>

---

<h2 align="center">Table of Contents 📚</h2>

- [Overview 📚](#overview-)
- [Quick Start 🚀](#quick-start-)
- [Installation 📦](#installation-)
- [Usage ⚙️](#usage-️)
- [Security & Privacy 🔒](#security--privacy-)
- [Links 🔗](#links-)

---

<h2 align="center">Overview 📚</h2>

<p align="center"><img src="https://raw.githubusercontent.com/Sang-Buster/Canvas-Sync/refs/heads/main/docs/images/overview.png" alt="Overview" /></p>

Canvas-Sync mirrors your Canvas course structure locally so you can browse course materials offline. It downloads modules, assignments, pages, files, and optional external resources into a tidy folder layout.

Key Features include: 
  - Automatic synchronization of modules, assignments, and files
  - Preserves course/module/subfolder structure locally
  - Configurable: choose which content types to sync
  - Optional download of external files referenced in descriptions
  - Simple, user-friendly CLI with interactive setup (Typer + Rich)
  - Rich progress bars and improved sync status output

---

<h2 align="center">Quick Start 🚀</h2>

### Step 1 — Generate a Canvas API token

- Log in to your Canvas instance → **Account** → **Settings** → **Approved Integrations** → **New Access Token**.
- Copy the token and keep it secure. You will use it during setup.

<p align="center"><img src="https://raw.githubusercontent.com/Sang-Buster/Canvas-Sync/refs/heads/main/docs/images/auth_token.png" alt="Auth Token" /></p>

### Step 2 — Install Canvas-Sync

See the [Installation](#installation-) section below for all options.

### Step 3 — Launch and configure

Run `canvas setup` to launch the interactive setup:

1. Choose a local sync folder
2. Provide your Canvas domain (without `https://`, e.g. `example.instructure.com`)
3. Enter the API token from Step 1
4. Select the courses to sync

After setup, run `canvas sync` to begin downloading course content.

---

<h2 align="center">Installation 📦</h2>

Pick the method that best fits your workflow:

**Using `uv` (recommended):**

```bash
uv add canvas-sync-py
uv pip install canvas-sync-py
```

**With `pip`:**

```bash
pip install canvas-sync-py
```

**From source (developer mode):**

```bash
git clone https://github.com/Sang-Buster/Canvas-Sync.git
cd Canvas-Sync
pip install -e .
PYTHONPATH=src canvas --help
```

---

<h2 align="center">Usage ⚙️</h2>

| Command         | Description                                                                   |
|-----------------|-------------------------------------------------------------------------------|
| `canvas --help` | Launch CLI and show help message                                              |
| `canvas setup`  | Re-run setup and update saved values                                          |
| `canvas info`   | Show current saved settings                                                   |
| `canvas sync`   | Start synchronization using saved settings                                    |
| `canvas reset`  | Reset and remove saved encrypted settings (use when you forgot your password) |

---

<h2 align="center">Security & Privacy 🔒</h2>

| Features                           | Description                                                                                                                 |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **Data stays local and encrypted** | All settings and your Canvas API token are stored locally on your device using AES encryption with a password-derived key.  |
| **Read-only access**               | Canvas-Sync only downloads course content — it never makes changes to your Canvas account.                                  |
| **Revoke access anytime**          | Use `canvas setup` to update your settings or `canvas reset` to delete them completely.                                     |
| **Protect your token**             | Never share your Canvas API token. If you believe it's compromised, revoke it in Canvas immediately and run `canvas reset`. |

---

<h2 align="center">Links 🔗</h2>

- Architecture notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Releases and changelog: [CHANGELOG.md](CHANGELOG.md)
