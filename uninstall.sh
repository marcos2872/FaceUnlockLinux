#!/bin/bash

# Script de Desinstalação do Face Unlock
echo "--- Iniciando Desinstalação do Face Unlock ---"

INSTALL_DIR="$HOME/.local/share/faceunlock"
DESKTOP_FILE="$HOME/.local/share/applications/faceunlock.desktop"
CONFIG_DIR="$HOME/.config/faceunlock"
CACHE_DIR="$HOME/.cache/faceunlock"
SYSTEM_DATA_DIR="/var/lib/faceunlock"
SYSTEM_LOG_DIR="/var/log/faceunlock"

# 0. Aviso de Segurança (PAM)
echo "IMPORTANTE: Antes de desinstalar, certifique-se de que desativou a integração facial no painel de controle do Face Unlock."
echo "Se você desinstalar com a integração ativa, poderá ter problemas para usar o sudo ou fazer login."
echo ""
read -p "Você já desativou as integrações de sistema? (sudo, login, etc) [s/N]: " pam_confirm
if [[ ! "$pam_confirm" =~ ^[sS]$ ]]; then
    echo "Operação cancelada. Por favor, desative as integrações no app primeiro."
    exit 1
fi

# 1. Remover Atalho do Menu
if [ -f "$DESKTOP_FILE" ]; then
    echo "1/4. Removendo atalho do menu ($DESKTOP_FILE)..."
    rm "$DESKTOP_FILE"
else
    echo "1/4. Atalho do menu não encontrado."
fi

# 2. Remover Arquivos da Aplicação
if [ -d "$INSTALL_DIR" ]; then
    echo "2/4. Removendo arquivos da aplicação em $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
else
    echo "2/4. Diretório de instalação não encontrado."
fi

# 3. Remover Configurações e Logs de Usuário
echo "3/4. Removendo configurações e logs locais..."
[ -d "$CONFIG_DIR" ] && rm -rf "$CONFIG_DIR"
[ -d "$CACHE_DIR" ] && rm -rf "$CACHE_DIR"

# 4. Remover Dados de Sistema (Requer Sudo)
echo "4/4. Limpando dados de sistema..."
if [ -d "$SYSTEM_DATA_DIR" ] || [ -d "$SYSTEM_LOG_DIR" ]; then
    read -p "Deseja remover também os rostos e logs de sistema (/var/lib e /var/log)? [s/N]: " confirm
    if [[ "$confirm" =~ ^[sS]$ ]]; then
        echo "Removendo dados de sistema (solicitando sudo)..."
        sudo rm -rf "$SYSTEM_DATA_DIR" "$SYSTEM_LOG_DIR"
    else
        echo "Mantendo dados de sistema (seus rostos cadastrados foram preservados)."
    fi
else
    echo "4/4. Diretórios de sistema não encontrados."
fi

echo ""
echo "--- Desinstalação Concluída! ---"
echo "O Face Unlock foi removido do seu sistema."
