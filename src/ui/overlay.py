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

            # Se rodando como root (PAM/Polkit), tenta rodar o overlay como o usuário real
            # No Linux, a variável SUDO_USER ou LOGNAME nos diz quem é o usuário real
            real_user = os.environ.get("SUDO_USER") or os.environ.get("LOGNAME")

            cmd = [python_exe, window_script, username]

            # Se somos root e sabemos quem é o usuário real, usamos 'sudo -u'
            if os.geteuid() == 0 and real_user and real_user != "root":
                cmd = ["sudo", "-u", real_user] + cmd

            # Lança o processo de forma independente
            self.process = subprocess.Popen(
                cmd,
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
