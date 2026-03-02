import os
import sys

import numpy as np

# Adicionar src ao path
sys.path.append(os.path.join(os.getcwd(), 'src'))
from storage import list_users, load_user_data, save_user_data


def test_storage():
    print("--- Testando Modelo de Dados ---")
    username = "test_user"
    
    # Criar 5 embeddings dummy de 128 dimensões
    dummy_embeddings = [np.random.rand(128) for _ in range(5)]
    
    print(f"Salvando dados para {username}...")
    meta_p, emb_p = save_user_data(username, dummy_embeddings)
    
    print(f"Arquivos criados:\n - {meta_p}\n - {emb_p}")
    
    # Recarregar
    loaded_embs, metadata = load_user_data(username)
    
    if loaded_embs is not None:
        print("Dados carregados com sucesso!")
        print(f"Usuário: {metadata['username']}")
        print(f"Número de embeddings: {len(loaded_embs)}")
        print(f"Shape: {loaded_embs.shape}")
        
        # Verificar se os dados são iguais (aproximadamente)
        if np.allclose(loaded_embs[0], dummy_embeddings[0]):
            print("Verificação de integridade: OK")
        else:
            print("ERRO: Dados corrompidos!")
    else:
        print("ERRO: Falha ao carregar dados.")
        
    print(f"Usuários cadastrados: {list_users()}")

if __name__ == "__main__":
    test_storage()
