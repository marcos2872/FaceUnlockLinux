import os
import json

CONFIG_PATH = os.path.expanduser("~/.config/faceunlock/settings.json")

DEFAULT_CONFIG = {
    "threshold": 0.5,
    "num_enrol_frames": 30,
    "num_auth_frames": 10
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
