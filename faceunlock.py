import argparse
import sys
import os

# Adicionar src ao path usando o caminho absoluto do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, 'src'))

from core import capture_embeddings, authenticate_user
from storage import save_user_data, load_user_data, list_users

def main():
    parser = argparse.ArgumentParser(description="Face Unlock - Sistema de Reconhecimento Facial")
    subparsers = parser.add_subparsers(dest="command")

    # Comando Enrol (Cadastro)
    enrol_parser = subparsers.add_parser("enrol", help="Cadastra um novo rosto")
    enrol_parser.add_argument("--user", required=True, help="Nome do usuário para cadastrar")
    enrol_parser.add_argument("--frames", type=int, default=30, help="Número de frames para capturar (padrão 30)")

    # Comando Auth (Autenticação)
    auth_parser = subparsers.add_parser("auth", help="Autentica um usuário cadastrado")
    auth_parser.add_argument("--user", required=True, help="Nome do usuário para autenticar")
    auth_parser.add_argument("--threshold", type=float, default=0.5, help="Distância máxima de tolerância (padrão 0.5)")
    auth_parser.add_argument("--no-gui", action="store_true", help="Executa sem abrir janela de vídeo (modo PAM)")

    # Comando List (Listar Usuários)
    list_parser = subparsers.add_parser("list", help="Lista usuários cadastrados")

    # Comando Init (Configuração de Sistema)
    init_parser = subparsers.add_parser("init", help="Configura diretórios de sistema (requer root)")

    args = parser.parse_args()

    if args.command == "init":
        SYSTEM_DIR = "/var/lib/faceunlock"
        print(f"Configurando diretório de sistema em {SYSTEM_DIR}...")
        
        try:
            # Tentar criar o diretório
            if not os.path.exists(SYSTEM_DIR):
                os.makedirs(SYSTEM_DIR, mode=0o700, exist_ok=True)
                print(f"Diretório {SYSTEM_DIR} criado com sucesso.")
            
            # Garantir permissões restritas (apenas root)
            os.chmod(SYSTEM_DIR, 0o700)
            print("Permissões 0700 (apenas root) aplicadas.")
            
            print("\nPronto! Agora o sistema usará /var/lib/faceunlock por padrão.")
            sys.exit(0)
            
        except PermissionError:
            print("\nErro de Permissão: Rode este comando com sudo!")
            sys.exit(1)
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            sys.exit(1)

    elif args.command == "enrol":
        # Captura os embeddings
        embeddings = capture_embeddings(args.user, args.frames)
        
        if embeddings and len(embeddings) > 0:
            print(f"Salvando {len(embeddings)} embeddings para '{args.user}'...")
            save_user_data(args.user, embeddings)
            print("Cadastro finalizado com sucesso!")
        else:
            print("Erro: Nenhum dado capturado.")

    elif args.command == "auth":
        # Carregar dados do usuário
        saved_embeddings, metadata = load_user_data(args.user)
        
        if saved_embeddings is None:
            print(f"Erro: Usuário '{args.user}' não encontrado. Use o comando 'enrol' primeiro.")
            sys.exit(1)
            
        # Executar a autenticação
        is_authenticated = authenticate_user(
            args.user, 
            saved_embeddings, 
            threshold=args.threshold,
            show_preview=not args.no_gui
        )
        
        if is_authenticated:
            print(f"\n[OK] Bem-vindo, {args.user}! Autenticação bem sucedida.")
            sys.exit(0)
        else:
            print(f"\n[FAIL] Autenticação falhou para {args.user}.")
            sys.exit(1)

    elif args.command == "list":
        users = list_users()
        if users:
            print("Usuários cadastrados:")
            for user in users:
                print(f" - {user}")
        else:
            print("Nenhum usuário cadastrado.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
