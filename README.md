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
- 📺 **Overlay de Feedback Visual**: Uma janela discreta no topo do monitor ativo que avisa quando o sistema está te procurando (ativo em `sudo` e `polkit`).
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

2. **Configurar Aplicativo** (Move para `~/.local`, configura `/var/lib` e cria atalho):
```bash
chmod +x setup_app.sh
./setup_app.sh
```

O sistema será movido para `~/.local/share/faceunlock` e um atalho será criado no seu menu de aplicativos. **No Fedora, o script aplica automaticamente o contexto SELinux (`chcon`) necessário.**

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
Você pode abrir o **Face Unlock** diretamente do seu menu de aplicativos. Ele solicitará sua senha (via `kdesu`) para permitir a modificação das regras de sistema (PAM).

- Vá em **Gerenciar Usuários** para cadastrar seu rosto.
- Vá em **Integração & Sistema** para habilitar o Face Unlock no `sudo`, `login` e `tela de bloqueio`.

### 2. Logs e Diagnóstico
Para verificar tentativas de acesso e erros de hardware:
- **Logs de Usuário**: `~/.cache/faceunlock/access.log`
- **Logs de Sistema (Root)**: `/var/log/faceunlock/access.log`

---

## 🔒 Segurança e Privacidade

- **Localização dos Dados**: Os rostos cadastrados são salvos em `/var/lib/faceunlock` (apenas root) ou em `data/faces/`.
- **Ambientes Restritos**: O overlay visual é desativado no Logon (SDDM) e na Tela de Bloqueio para evitar falhas gráficas, rodando de forma silenciosa e segura nesses ambientes.
- **Fallback Automático**: Se a câmera não for encontrada ou falhar, o sistema pula imediatamente para o prompt de senha.

---

## 🛠️ Desenvolvimento e Qualidade de Código

Este projeto utiliza **Ruff** para linting e formatação, e **pre-commit** para garantir a qualidade do código.

### Comandos úteis:
- **Formatar código**: `./venv/bin/ruff format .`
- **Verificar erros**: `./venv/bin/ruff check --fix .`

---

## ⚠️ Isenção de Responsabilidade

Este projeto foi desenvolvido para fins de conveniência e aprendizado. Embora a detecção de vivacidade aumente a segurança, sistemas de reconhecimento facial baseados em webcams 2D podem não ser 100% imunes a ataques sofisticados. Sempre mantenha sua senha de usuário ativa como fallback.
