import logging
import os

LOG_DIR = os.path.expanduser("~/.cache/faceunlock")
LOG_FILE = os.path.join(LOG_DIR, "access.log")
SYSTEM_LOG_DIR = "/var/log/faceunlock"
SYSTEM_LOG_FILE = os.path.join(SYSTEM_LOG_DIR, "access.log")


def setup_logger():
    # Se rodando como root, tenta usar o log do sistema
    if os.geteuid() == 0:
        try:
            if not os.path.exists(SYSTEM_LOG_DIR):
                os.makedirs(SYSTEM_LOG_DIR, exist_ok=True)
            logging.basicConfig(filename=SYSTEM_LOG_FILE, level=logging.INFO, format="%(message)s")
            return
        except Exception:
            pass

    # Fallback para o log do usuário
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR, exist_ok=True)
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(message)s")
    except (PermissionError, OSError):
        # Se falhar em ambos, desativa o logging para não quebrar o PAM
        logging.basicConfig(handlers=[logging.NullHandler()], level=logging.INFO)


def log_access(username, success, message=""):
    setup_logger()
    from datetime import datetime

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status_icon = "✅ SUCCESS" if success else "❌ FAILED"
    separator = "-" * 50

    # Log estruturado com espaçamento
    log_entry = (
        f"\n{separator}\n"
        f"📅 Date: {now}\n"
        f"👤 User: {username}\n"
        f"🛡️ Status: {status_icon}\n"
        f"📝 Details: {message}\n"
        f"{separator}"
    )

    logging.info(log_entry)


def get_last_logs(limit=20):
    if not os.path.exists(LOG_FILE):
        return ["Nenhum log encontrado."]

    try:
        with open(LOG_FILE) as f:
            content = f.read()
            # Retornar o conteúdo formatado
            return content
    except Exception as e:
        return [f"Erro ao ler logs: {e}"]
