# Face Unlock para Linux (Fedora KDE) 🚀

O **Face Unlock** é um sistema de autenticação facial robusto escrito em Python, projetado especificamente para distros Linux (focado em Fedora KDE). Ele permite que você use sua webcam para autenticar o comando `sudo`, desbloquear a tela e fazer login no sistema.

---

## ✨ Funcionalidades

- 📸 **Cadastro Facial Interativo**: Interface gráfica simples para cadastrar seu rosto em segundos.
- 🛡️ **Integração com PAM**: Automatiza a configuração para que o `sudo` e a `Lock Screen` usem seu rosto.
- 👁️ **Detecção de Vivacidade (Liveness)**: Exige que você pisque os olhos para evitar que fotos ou vídeos enganem o sistema.
- 📊 **Painel de Controle Desktop**: Gerencie usuários, ajuste a sensibilidade e visualize logs de acesso.
- 🕵️ **Auditoria Completa**: Logs detalhados de todas as tentativas de acesso (sucessos e falhas).

---

## 🛠️ Requisitos de Sistema

- **OS**: Fedora Linux (testado na versão 43 KDE Plasma).
- **Python**: 3.10 ou superior (testado no 3.14).
- **Hardware**: Webcam funcional.
- **Dependências Nativas**: `cmake`, `gcc-c++`, `openblas-devel`, `libX11-devel`, `gtk3-devel`.

---

## 🚀 Instalação Rápida

Clone o repositório e execute o script de instalação automatizada:

```bash
git clone <url-do-repositorio>
cd FaceUnlock
chmod +x install.sh
./install.sh
```

O script cuidará de instalar as dependências de sistema, criar o ambiente virtual, compilar as bibliotecas de IA e configurar os diretórios protegidos.

---

## 🖥️ Como Usar

### 1. Interface Gráfica (Recomendado)
Para gerenciar suas faces e configurar o sistema:
```bash
# Para configurações de sistema (PAM), rode com sudo
sudo ./venv/bin/python gui.py
```
- Vá em **Gerenciar Faces** para cadastrar seu primeiro rosto.
- Vá em **Integração & Sistema** para habilitar o Face Unlock no `sudo`.

### 2. Linha de Comando (CLI)
O sistema também pode ser operado via terminal:
```bash
# Cadastro
./venv/bin/python faceunlock.py enrol --user seu_nome

# Autenticação (Modo teste)
./venv/bin/python faceunlock.py auth --user seu_nome

# Autenticação (Modo PAM - sem janela)
./venv/bin/python faceunlock.py auth --user seu_nome --no-gui
```

---

## 🔒 Segurança e Privacidade

- **Localização dos Dados**: Os rostos cadastrados são salvos em `/var/lib/faceunlock` (com permissões `700`, apenas root pode ler) ou em `data/faces/` em modo de desenvolvimento.
- **Formato de Dados**: Não salvamos fotos. Salvamos apenas **embeddings** (vetores matemáticos de 128 dimensões) que representam sua face.
- **Liveness Detection**: O sistema calcula o *Eye Aspect Ratio (EAR)* em tempo real. O acesso só é liberado se o sistema detectar pelo menos uma piscada real.

---

## 📁 Estrutura do Projeto

- `faceunlock.py`: Ponto de entrada do CLI.
- `gui.py`: Painel de controle desktop (PySide6).
- `src/`:
    - `core.py`: Lógica principal de reconhecimento facial.
    - `liveness.py`: Algoritmo de detecção de piscada.
    - `storage.py`: Gerenciamento de arquivos e vetores.
    - `system_integration.py`: Automação de arquivos PAM (`/etc/pam.d/`).
    - `logger.py`: Sistema de auditoria e histórico de acessos.
- `NEXT_STEPS.md`: Guia para configurações avançadas manuais.

---

## ⚠️ Isenção de Responsabilidade

Este projeto foi desenvolvido para fins de conveniência e aprendizado. Embora a detecção de vivacidade aumente a segurança, sistemas de reconhecimento facial baseados em webcams 2D podem não ser 100% imunes a ataques sofisticados. Sempre mantenha sua senha de usuário ativa como fallback.
