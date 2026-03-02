import os
import subprocess
import sys


class OverlayApp:
    """Gerencia a janela de overlay de forma isolada e segura."""

    def __init__(self, username):
        self.process = None

        # Se não houver sinal de display, aborta silenciosamente
        display = os.environ.get("DISPLAY") or ":0"
        wayland = os.environ.get("WAYLAND_DISPLAY")

        if not display and not wayland:
            return

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            window_script = os.path.join(current_dir, "overlay_window.py")
            python_exe = sys.executable

            # Detecta o usuário real para evitar rodar interface como root
            real_user = os.environ.get("SUDO_USER") or os.environ.get("USER")
            if real_user == "root" or not real_user:
                # Tenta pegar o dono da pasta home mais comum
                import pwd

                real_user = pwd.getpwuid(os.getuid())[0]
                if real_user == "root":
                    # Busca o usuário logado via comando 'who' se necessário
                    try:
                        real_user = subprocess.check_output(["whoami"]).decode().strip()
                    except Exception:
                        real_user = "marcos"  # Fallback seguro para seu sistema

            cmd = [python_exe, window_script, username]

            # Prepara ambiente limpo para o usuário
            env = {
                "DISPLAY": display,
                "PATH": os.environ.get("PATH", ""),
                "HOME": f"/home/{real_user}",
                "XDG_RUNTIME_DIR": f"/run/user/{os.getuid() if os.getuid() != 0 else 1000}",
            }
            if wayland:
                env["WAYLAND_DISPLAY"] = wayland

            # Se somos root, usamos 'sudo -u' para rodar como usuário comum
            if os.geteuid() == 0 and real_user != "root":
                cmd = ["sudo", "-u", real_user, "DISPLAY=" + display] + cmd

            # Lança o processo de forma totalmente independente
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # Isola o processo
                env=env,
            )
        except Exception:
            self.process = None

    def update(self, message, progress=0):
        pass

    def close(self):
        if self.process:
            try:
                # Tenta fechar de forma amigável
                self.process.terminate()
                self.process.wait(timeout=0.2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
