# Face Unlock - Project Mandates

This document serves as the foundational guide for AI assistants working on the Face Unlock project. These instructions take precedence over general defaults.

## 🏗️ Architecture & Organization
- **Modular UI**: All new GUI components must be placed in `src/ui/`. The main `gui.py` should only act as a high-level orchestrator.
- **Dependency Management**: System dependencies are handled by `install_deps.sh`. Application installation/movement logic resides in `setup_app.sh`.
- **Paths**: 
    - Application files: `~/.local/share/faceunlock/`
    - System/Security data: `/var/lib/faceunlock/` (Requires root)
    - Configuration: `~/.config/faceunlock/`
    - Logs: `~/.cache/faceunlock/`

## 🛡️ Security & Privacy
- **No Photos**: Never store raw images or video frames on disk. Only 128-dimensional face embeddings are permitted for storage.
- **PAM Safety**: Any modification to `/etc/pam.d/` files is critical. Always verify the existence of fallback authentication methods before suggesting or applying PAM changes.
- **Permissions**: `SYSTEM_DIR` (/var/lib/faceunlock) must always maintain `700` permissions.

## 🎨 UI & Aesthetics
- **Branding**: Always use `@images/icon.png` for window icons and `@images/logo.png` for documentation or splash screens.
- **Framework**: Use PySide6 for all GUI elements. Keep the modular "Tab-based" structure for the main panel.
- **Feedback**: Ensure every long-running operation (like face enrollment) has clear visual feedback (Progress bars, status labels).

## 🐍 Coding Standards
- **Python**: Target Python 3.10+. Be mindful of compatibility with higher versions (e.g., the 3.14 patch in `install_deps.sh`).
- **Imports**: Add `src` and `src/ui` to `sys.path` in entry points (`gui.py`, `faceunlock.py`) to maintain clean imports.
- **Validation**: Every feature or bug fix must be accompanied by a validation step, ideally using the existing GUI or CLI test commands.

## 📝 Git & Commit Standards
- **Conventional Commits**: Adhere to the Conventional Commits specification for all commit messages.
    - `feat:`: New features.
    - `fix:`: Bug fixes.
    - `docs:`: Documentation changes.
    - `style:`: Formatting, missing semi-colons, etc.; no code changes.
    - `refactor:`: Refactoring production code.
    - `test:`: Adding missing tests, refactoring tests; no production code change.
    - `chore:`: Updating build tasks, package manager configs, etc.; no production code change.
- **Quality Control**: Always run `pre-commit run --all-files` (which includes `ruff` linting and formatting) before finalizing changes or committing.
- **Language**: Commit descriptions should be concise and preferred in Portuguese, following the project's current trend.
