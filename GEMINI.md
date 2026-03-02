# Face Unlock - Project Mandates

This document serves as the foundational guide for AI assistants working on the Face Unlock project. These instructions take precedence over general defaults.

## 🏗️ Architecture & Organization
- **Modular UI**: All new GUI components must be placed in `src/ui/`. The main `gui.py` should only act as a high-level orchestrator.
- **Process Isolation**: The visual feedback (Overlay) **must** run in a separate process (`src/ui/overlay_window.py`) managed by `src/ui/overlay.py`. This prevents graphical crashes (very common in PAM/Polkit environments) from killing the authentication engine.
- **Paths**: 
    - Application files: `~/.local/share/faceunlock/`
    - System/Security data: `/var/lib/faceunlock/` (Requires root)
    - Configuration: `~/.config/faceunlock/`
    - Logs: `~/.cache/faceunlock/`

## 🛡️ Security & Privacy
- **No Photos**: Never store raw images or video frames on disk. Only 128-dimensional face embeddings are permitted for storage.
- **PAM/Polkit Safety**: Any modification to `/etc/pam.d/` files is critical. When removing lines, use robust pattern matching (searching for `faceunlock.py auth --user`) instead of exact string matching.
- **Root Context**: When launching graphical elements from a root process (Sudo/Polkit), always attempt to use `sudo -u <real_user>` to avoid X11/Wayland display restrictions.

## 🎨 UI & Aesthetics
- **Dark Mode**: The application uses a global Dark Theme (Fusion style) defined in `gui.py`. Avoid hardcoding bright colors in child components.
- **Overlay**: Visual feedback should be centered on the active monitor (detected via cursor position).
- **Feedback**: Ensure every long-running operation has clear visual feedback (Progress bars, notifications, or overlays).

## 🐍 Coding Standards
- **Python**: Target Python 3.10+.
- **Imports**: Use `# noqa: E402` for late imports required by `sys.path` modifications.
- **Validation**: Every feature or bug fix must be verified through both CLI and GUI manual tests.

## 📝 Git & Commit Standards
- **Conventional Commits**: Adhere to the Conventional Commits specification.
    - `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`.
- **Quality Control**: Always run `pre-commit run --all-files` (which includes `ruff` linting and formatting) before finalizing changes.
- **Language**: Commit descriptions should be concise and preferred in Portuguese.
