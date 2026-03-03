import json
import os

SYSTEM_CONFIG_DIR = "/var/lib/faceunlock"
SYSTEM_CONFIG_PATH = os.path.join(SYSTEM_CONFIG_DIR, "settings.json")
USER_CONFIG_PATH = os.path.expanduser("~/.config/faceunlock/settings.json")

# Prioriza o local de sistema se ele existir e for gravável (ou se estivermos como root)
if os.path.exists(SYSTEM_CONFIG_DIR) and (
    os.access(SYSTEM_CONFIG_DIR, os.W_OK) or os.geteuid() == 0
):
    CONFIG_PATH = SYSTEM_CONFIG_PATH
else:
    CONFIG_PATH = USER_CONFIG_PATH

DEFAULT_CONFIG = {"threshold": 0.5, "num_enrol_frames": 30, "num_auth_frames": 10}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
