import logging
import os

LOG_DIR = os.path.expanduser("~/.cache/faceunlock")
LOG_FILE = os.path.join(LOG_DIR, "access.log")


def setup_logger():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

    # Configuração do logger para adicionar apenas a mensagem
    # formatamos a data manualmente para ter mais controle
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(message)s")


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
