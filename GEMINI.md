# Face Unlock - Project Mandates

This document serves as the foundational guide for AI assistants working on the Face Unlock project. These instructions take precedence over general defaults.

## 🏗️ Architecture & Organization
- **Modular UI**: All new GUI components must be placed in `src/ui/`. The main `gui.py` should only act as a high-level orchestrator.
- **Process Isolation**: The visual feedback (Overlay) **must** run in a separate process (`src/ui/overlay_window.py`) managed by `src/ui/overlay.py`. This prevents graphical crashes (very common in PAM/Polkit environments) from killing the authentication engine.
- **Paths**: 
    - Application files: `~/.local/share/faceunlock/`
    - System/Security data: `/var/lib/faceunlock/` (Requires root)
    - Configuration: `~/.config/faceunlock/settings.json` (User) ou `/var/lib/faceunlock/settings.json` (Sistema - Prioritário).
    - Logs: `~/.cache/faceunlock/` (User) ou `/var/log/faceunlock/` (Sistema).

## 🛡️ Security & Privacy
- **No Photos**: Never store raw images or video frames on disk. Only 128-dimensional face embeddings are permitted for storage.
- **PAM/Polkit Safety**: Any modification to `/etc/pam.d/` files is critical. Quando removendo linhas, use padrões flexíveis (`faceunlock.py auth --user`) para identificar a integração.
- **Root Context**: Quando lançando elementos gráficos de um processo root (Sudo/Polkit), sempre tente usar `sudo -u <real_user>` para evitar restrições de display X11/Wayland.
- **Selective Overlay**: O overlay gráfico deve ser desabilitado para serviços de logon (SDDM) e tela de bloqueio (kscreenlocker) para evitar crashes fatais de ambiente gráfico root. Use apenas em `sudo` e `polkit`.

## 🎨 UI & Aesthetics
- **Dark Mode**: A aplicação usa o tema global Dark (estilo Fusion) definido em `gui.py`. Evite hardcoding de cores claras.
- **Overlay**: O feedback visual deve ser centralizado no monitor ativo.
- **Async Camera**: A inicialização da câmera deve ser assíncrona (via QTimer) para evitar que a interface gráfica fique "Não Respondendo" durante o carregamento do sensor.

## 🐍 Coding Standards
- **Python**: Alvo Python 3.10+.
- **Imports**: Use `# noqa: E402` para imports tardios exigidos por modificações no `sys.path`.
- **Validation**: Toda feature ou correção deve ser validada via CLI e GUI. Em caso de falha de hardware (câmera), o sistema deve retornar `False` imediatamente para permitir o fallback de senha no PAM.

## 📝 Git & Commit Standards
- **Conventional Commits**: Siga a especificação Conventional Commits.
    - `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`.
- **Quality Control**: Sempre rode `pre-commit run --all-files` (ruff linting e format) antes de finalizar mudanças.
- **Language**: Descrições de commit concisas e preferencialmente em Português.
