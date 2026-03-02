<p align="center">
  <img src="images/logo.png" alt="Face Unlock Logo" width="600">
</p>

# Face Unlock para Linux (Fedora KDE) 🚀

O **Face Unlock** é um sistema de autenticação facial robusto escrito em Python, projetado especificamente para distros Linux (focado em Fedora KDE). Ele permite que você use sua webcam para autenticar o comando `sudo`, desbloquear a tela e fazer login no sistema.

---

## ✨ Funcionalidades

- 📸 **Cadastro Facial Interativo**: Interface gráfica simples para cadastrar seu rosto em segundos.
- 🛡️ **Integração com PAM & Polkit**: Automatiza a configuração para que o `sudo`, a `Lock Screen` e até **Ações de Administrador** (como montar discos) usem seu rosto.
- 👁️ **Detecção de Vivacidade (Liveness)**: Exige que você pisque os olhos para evitar que fotos ou vídeos enganem o sistema.
- 📺 **Overlay de Feedback Visual**: Uma janela discreta no topo do monitor ativo que avisa quando o sistema está te procurando durante autenticações silenciosas.
- 🌑 **Modo Escuro (Dark Mode)**: Interface moderna e consistente, mesmo quando executada como root.
- 📊 **Painel de Controle Desktop**: Gerencie usuários, ajuste a sensibilidade e visualize logs de acesso.

---

## 🛠️ Requisitos de Sistema

- **OS**: Fedora Linux (testado na versão 43 KDE Plasma).
- **Python**: 3.10 ou superior (testado no 3.14).
- **Hardware**: Webcam funcional.
- **Dependências Nativas**: `cmake`, `gcc-c++`, `openblas-devel`, `libX11-devel`, `gtk3-devel`.

---

## 🚀 Instalação Rápida

Clone o repositório e execute os scripts de instalação em ordem:

1. **Instalar dependências** (Sistema e IA):
```bash
chmod +x install_deps.sh
./install_deps.sh
```

2. **Configurar Aplicativo** (Move para `~/.local` e cria atalho no menu):
```bash
chmod +x setup_app.sh
./setup_app.sh
```

O sistema será movido para `~/.local/share/faceunlock` e um atalho será criado no seu menu de aplicativos (KDE/Gnome/etc).

---

## 🗑️ Desinstalação

Se precisar remover o sistema e todos os seus dados:
```bash
chmod +x uninstall.sh
./uninstall.sh
```

---

## 🖥️ Como Usar

### 1. Interface Gráfica (Recomendado)
Você pode abrir o **Face Unlock** diretamente do seu menu de aplicativos ou via terminal:
```bash
# Para aplicar integrações de sistema, rode com sudo
sudo ~/.local/share/faceunlock/venv/bin/python ~/.local/share/faceunlock/gui.py
```
- Vá em **Gerenciar Faces** para cadastrar seu primeiro rosto.
- Vá em **Integração & Sistema** para habilitar o Face Unlock no `sudo` e no `Polkit`.

### 2. Linha de Comando (CLI)
O sistema também pode ser operado via terminal a partir do diretório de instalação:
```bash
cd ~/.local/share/faceunlock
# Cadastro
./venv/bin/python faceunlock.py enrol --user seu_nome

# Autenticação (Modo teste)
./venv/bin/python faceunlock.py auth --user seu_nome

# Autenticação (Modo PAM - com overlay visual)
./venv/bin/python faceunlock.py auth --user seu_nome --no-gui --overlay
```

---

## 🔒 Segurança e Privacidade

- **Localização dos Dados**: Os rostos cadastrados são salvos em `/var/lib/faceunlock` (com permissões `700`, apenas root pode ler) ou em `data/faces/` em modo de desenvolvimento.
- **Isolamento de Processos**: O feedback visual (overlay) roda em um processo separado para garantir que falhas gráficas não interrompam a autenticação.
- **Formato de Dados**: Não salvamos fotos. Salvamos apenas **embeddings** (vetores matemáticos de 128 dimensões).

---

## 🛠️ Desenvolvimento e Qualidade de Código

Este projeto utiliza **Ruff** para linting e formatação, e **pre-commit** para garantir a qualidade do código.

### Comandos úteis:
- **Formatar código**: `./venv/bin/ruff format .`
- **Verificar erros**: `./venv/bin/ruff check --fix .`
- **Instalar hooks**: `./venv/bin/pre-commit install`

---

## 📁 Estrutura do Projeto

- `faceunlock.py`: Ponto de entrada do CLI e motor PAM.
- `gui.py`: Janela principal do Painel de Controle.
- `src/`:
    - `core.py`: Lógica principal de reconhecimento e autenticação.
    - `storage.py`: Gerenciamento de arquivos e vetores (Multi-local).
    - `system_integration.py`: Automação de PAM e Polkit.
    - `ui/`:
        - `faces_tab.py`, `test_tab.py`, `settings_tab.py`: Componentes da GUI.
        - `overlay.py`: Gerenciador do feedback visual.
        - `overlay_window.py`: Janela de overlay (processo isolado).

---

## ⚠️ Isenção de Responsabilidade

Este projeto foi desenvolvido para fins de conveniência e aprendizado. Embora a detecção de vivacidade aumente a segurança, sistemas de reconhecimento facial baseados em webcams 2D podem não ser 100% imunes a ataques sofisticados. Sempre mantenha sua senha de usuário ativa como fallback.
