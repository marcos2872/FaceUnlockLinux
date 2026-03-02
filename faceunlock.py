import argparse
import os
import sys

# Adicionar src ao path usando o caminho absoluto do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, 'src'))

from core import authenticate_user, capture_embeddings
from logger import log_access
from storage import list_users, load_user_data, save_user_data


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
    subparsers.add_parser("list", help="Lista usuários cadastrados")

    # Comando Init (Configuração de Sistema)
    subparsers.add_parser("init", help="Configura diretórios de sistema (requer root)")

    args = parser.parse_args()

    if args.command == "init":
        SYSTEM_DIR = "/var/lib/faceunlock"
        print(f"Configurando diretório de sistema em {SYSTEM_DIR}...")
        try:
            if not os.path.exists(SYSTEM_DIR):
                os.makedirs(SYSTEM_DIR, mode=0o700, exist_ok=True)
            os.chmod(SYSTEM_DIR, 0o700)
            print("Sucesso! Diretório de sistema pronto.")
            sys.exit(0)
        except Exception as e:
            print(f"Erro: {e}")
            sys.exit(1)

    elif args.command == "enrol":
        embeddings = capture_embeddings(args.user, args.frames)
        if embeddings and len(embeddings) > 0:
            save_user_data(args.user, embeddings)
            print("Cadastro finalizado com sucesso!")
        else:
            print("Erro: Nenhum dado capturado.")

    elif args.command == "auth":
        saved_embeddings, metadata = load_user_data(args.user)
        if saved_embeddings is None:
            print(f"Erro: Usuário '{args.user}' não encontrado.")
            sys.exit(1)
            
        is_authenticated = authenticate_user(
            args.user, 
            saved_embeddings, 
            threshold=args.threshold,
            show_preview=not args.no_gui
        )
        
        # Logar o acesso (essencial para o PAM)
        access_type = "PAM (No-GUI)" if args.no_gui else "Manual CLI"
        log_access(args.user, is_authenticated, f"{access_type} | Threshold: {args.threshold}")
        
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
            for user in users: print(f" - {user}")
        else:
            print("Nenhum usuário cadastrado.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
