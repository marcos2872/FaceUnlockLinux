import os
import subprocess
import sys


class OverlayApp:
    """Gerencia feedback visual (Janela ou Notificação) de forma segura."""

    def __init__(self, username):
        self.process = None

        # 1. Tentar enviar uma notificação de sistema (Garantia visual)
        try:
            # notify-send é padrão no Fedora/KDE
            subprocess.Popen(
                [
                    "notify-send",
                    "-a",
                    "Face Unlock",
                    "-i",
                    "camera-photo",
                    "Face Unlock",
                    f"Iniciando reconhecimento para {username}...",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

        # 2. Tentar abrir a janela de overlay (Feedback detalhado)
        display = os.environ.get("DISPLAY") or ":0"
        wayland = os.environ.get("WAYLAND_DISPLAY")

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            window_script = os.path.join(current_dir, "overlay_window.py")
            python_exe = sys.executable

            # Busca o usuário real (UID 1000 é o padrão do primeiro usuário)
            import pwd

            try:
                real_user_info = pwd.getpwuid(1000)
                real_user = real_user_info.pw_name
            except Exception:
                real_user = os.environ.get("SUDO_USER") or "marcos"

            cmd = [python_exe, window_script, username]

            # Ambiente isolado para o usuário comum
            env = os.environ.copy()
            env["DISPLAY"] = display
            if wayland:
                env["WAYLAND_DISPLAY"] = wayland
            env["XDG_RUNTIME_DIR"] = "/run/user/1000"

            # Se somos root, tentamos lançar como o usuário comum
            if os.geteuid() == 0:
                cmd = ["sudo", "-u", real_user] + cmd

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env=env,
            )
        except Exception:
            self.process = None

    def update(self, message, progress=0):
        pass

    def close(self):
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
