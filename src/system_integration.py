import os
import sys

PAM_SERVICES = {
    "sudo": "/etc/pam.d/sudo",
    "lockscreen": "/etc/pam.d/kde",
    "login": "/etc/pam.d/sddm",
    "polkit": "/etc/pam.d/polkit-1",
}


def get_pam_line(username):
    """Gera a linha exata que deve ser inserida no PAM."""
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "faceunlock.py"
    )
    python_path = sys.executable  # Usa o python do venv atual
    return (
        f"auth sufficient pam_exec.so stdout {python_path} {script_path} "
        f"auth --user {username} --no-gui"
    )


def check_integration(service_name, username):
    """Verifica se a integração existe no arquivo do PAM de forma flexível."""
    path = PAM_SERVICES.get(service_name)
    if not path:
        return False

    # Se não existe em /etc, tenta ler do original em /usr/lib
    if not os.path.exists(path):
        path = os.path.join("/usr/lib/pam.d", os.path.basename(path))

    if not os.path.exists(path):
        return False

    # Busca por termos essenciais em vez da linha exata
    search_term = f"faceunlock.py auth --user {username}"
    try:
        with open(path) as f:
            for line in f:
                if search_term in line and "pam_exec.so" in line:
                    return True
            return False
    except PermissionError:
        return "Permission Denied"
    except Exception:
        return False


def update_integration(service_name, username, enable=True):
    """Adiciona ou remove a linha do PAM. Requer root."""
    path = PAM_SERVICES.get(service_name)
    line = get_pam_line(username)

    if not path:
        return False, f"Serviço {service_name} não configurado."

    # No Fedora, se o arquivo não existe em /etc/pam.d/, tentamos ler de /usr/lib/pam.d/
    if not os.path.exists(path):
        fallback_path = os.path.join("/usr/lib/pam.d", os.path.basename(path))
        if os.path.exists(fallback_path):
            try:
                # Cria o diretório em /etc se necessário (raro)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                # Lê o conteúdo do fallback para o novo arquivo em /etc
                with open(fallback_path) as f:
                    content = f.read()
                with open(path, "w") as f:
                    f.write(content)
            except PermissionError:
                return (
                    False,
                    "Erro de permissão ao criar arquivo em /etc/pam.d/. Execute como root.",
                )
        else:
            return False, f"Arquivo de serviço {service_name} não encontrado em /etc ou /usr/lib."

    try:
        with open(path) as f:
            lines = f.readlines()

        # Remover linha se já existir (para atualizar ou desabilitar)
        new_lines = [line_item for line_item in lines if line not in line_item]

        if enable:
            # Inserir no topo (após o cabeçalho)
            index = 0
            if len(new_lines) > 0 and new_lines[0].startswith("#%PAM"):
                index = 1
            new_lines.insert(index, line + "\n")

        with open(path, "w") as f:
            f.writelines(new_lines)

        return True, "Configuração atualizada."
    except PermissionError:
        return False, "Erro de permissão. Execute como root."
    except Exception as e:
        return False, str(e)
