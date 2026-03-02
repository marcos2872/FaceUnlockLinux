import os
import json
import numpy as np
from datetime import datetime

# Caminhos padrão
SYSTEM_DIR = "/var/lib/faceunlock"
# Local absoluto da pasta data dentro do projeto
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DIR = os.path.join(SCRIPT_DIR, "data", "faces")

# Escolher o diretório base (prioriza o de sistema se existir)
if os.path.exists(SYSTEM_DIR) and os.access(SYSTEM_DIR, os.W_OK):
    BASE_DIR = SYSTEM_DIR
else:
    BASE_DIR = LOCAL_DIR

def get_user_path(username):
    """Retorna o caminho da pasta do usuário."""
    return os.path.join(BASE_DIR, username)

def save_user_data(username, embeddings, threshold=0.6, model_version="dlib_v1"):
    """
    Salva os embeddings (NumPy) e metadados (JSON).
    embeddings: lista ou array de shape (N, 128)
    """
    user_dir = get_user_path(username)
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
        "num_embeddings": len(embeddings)
    }
    
    with open(meta_path, 'w', encoding='utf-8') as f:
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
    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    return embeddings, metadata

def list_users():
    """Lista usuários cadastrados."""
    if not os.path.exists(BASE_DIR):
        return []
    return [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

def delete_user(username):
    """Remove a pasta do usuário e todos os seus dados."""
    import shutil
    user_dir = get_user_path(username)
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
        return True
    return False
