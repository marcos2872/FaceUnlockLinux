import json
import os
from datetime import datetime

import numpy as np

# Caminhos padrão
SYSTEM_DIR = "/var/lib/faceunlock"
# Local absoluto da pasta data dentro do projeto
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DIR = os.path.join(SCRIPT_DIR, "data", "faces")


def get_base_dir():
    """Retorna o diretório base preferencial para gravação."""
    if os.path.exists(SYSTEM_DIR) and os.access(SYSTEM_DIR, os.W_OK):
        return SYSTEM_DIR
    return LOCAL_DIR


def get_user_path(username):
    """Retorna o caminho da pasta do usuário (Sistema ou Local)."""
    # 1. Tenta no diretório de sistema (/var/lib/faceunlock/nome_do_usuario)
    sys_path = os.path.join(SYSTEM_DIR, username)
    if os.path.exists(sys_path):
        return sys_path

    # 2. Se não existir, tenta no diretório local do projeto
    local_path = os.path.join(LOCAL_DIR, username)
    return local_path


def save_user_data(username, embeddings, threshold=0.6, model_version="dlib_v1"):
    """
    Salva os embeddings (NumPy) e metadados (JSON).
    embeddings: lista ou array de shape (N, 128)
    """
    # Para novos cadastros, tenta usar o diretório base preferencial
    base_dir = get_base_dir()
    user_dir = os.path.join(base_dir, username)

    # Se o usuário já existir no outro diretório, continua usando o existente
    existing_dir = get_user_path(username)
    if os.path.exists(existing_dir):
        user_dir = existing_dir

    os.makedirs(user_dir, exist_ok=True)

    # Caminhos
    emb_path = os.path.join(user_dir, "embeddings.npy")
    meta_path = os.path.join(user_dir, "metadata.json")

    # Salvar embeddings em formato binário (.npy)
    np.save(emb_path, np.array(embeddings))

    # Preparar e salvar metadados
    metadata = {
        "username": username,
        "created_at": datetime.now().isoformat(),
        "model_version": model_version,
        "threshold": threshold,
        "num_embeddings": len(embeddings),
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    return meta_path, emb_path


def load_user_data(username):
    """
    Carrega embeddings e metadados do usuário.
    Retorna (embeddings, metadata) ou (None, None) se não existir.
    """
    user_dir = get_user_path(username)
    emb_path = os.path.join(user_dir, "embeddings.npy")
    meta_path = os.path.join(user_dir, "metadata.json")

    if not os.path.exists(emb_path) or not os.path.exists(meta_path):
        return None, None

    embeddings = np.load(emb_path)
    with open(meta_path, encoding="utf-8") as f:
        metadata = json.load(f)

    return embeddings, metadata


def list_users():
    """Lista usuários cadastrados em ambos os diretórios (Sistema e Local)."""
    users = set()

    # Busca no diretório de sistema
    if os.path.exists(SYSTEM_DIR):
        try:
            for d in os.listdir(SYSTEM_DIR):
                if os.path.isdir(os.path.join(SYSTEM_DIR, d)):
                    users.add(d)
        except PermissionError:
            pass

    # Busca no diretório local do projeto
    if os.path.exists(LOCAL_DIR):
        try:
            for d in os.listdir(LOCAL_DIR):
                if os.path.isdir(os.path.join(LOCAL_DIR, d)):
                    users.add(d)
        except PermissionError:
            pass

    return sorted(list(users))


def delete_user(username):
    """Remove a pasta do usuário e todos os seus dados."""
    import shutil

    user_dir = get_user_path(username)
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
        return True
    return False
