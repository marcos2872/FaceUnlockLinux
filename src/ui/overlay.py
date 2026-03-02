import os
import subprocess
import sys


class OverlayApp:
    """Gerencia a janela de overlay como um processo externo para evitar crash fatal no PAM."""

    def __init__(self, username):
        self.process = None

        # Só tenta se houver display
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            return

        try:
            # Localiza o script da janela
            current_dir = os.path.dirname(os.path.abspath(__file__))
            window_script = os.path.join(current_dir, "overlay_window.py")
            python_exe = sys.executable

            # Lança o processo de forma independente
            # Usamos subprocess para que um crash gráfico não afete a IA
            self.process = subprocess.Popen(
                [python_exe, window_script, username],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=os.environ.copy(),
            )
        except Exception:
            self.process = None

    def update(self, message, progress=0):
        # O update visual via processo externo exigiria IPC (sockets/pipes).
        # Por enquanto, focamos na estabilidade (abrir e fechar a janela).
        pass

    def close(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=0.5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
