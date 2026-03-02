#!/bin/bash

# Script de Configuração do Face Unlock
echo "--- Configurando Face Unlock no Sistema ---"

INSTALL_DIR="$HOME/.local/share/faceunlock"
DESKTOP_DIR="$HOME/.local/share/applications"

# 1. Preparar Diretório de Instalação
echo "1/4. Movendo arquivos para $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
# Copia tudo para o local final (exceto o próprio instalador e arquivos git se existirem)
cp -r . "$INSTALL_DIR"

# 2. Inicializar diretórios de sistema
echo "2/4. Inicializando diretórios de sistema (/var/lib/faceunlock)..."
sudo "$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/faceunlock.py" init

# 3. Gerar e Instalar o Arquivo .desktop
echo "3/4. Instalando ícone e atalho no menu do sistema..."
mkdir -p "$DESKTOP_DIR"

cat <<EOF > "$DESKTOP_DIR/faceunlock.desktop"
[Desktop Entry]
Name=Face Unlock
Comment=Gerenciar Autenticação Facial
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/gui.py
Icon=$INSTALL_DIR/images/icon.png
Terminal=false
Type=Application
Categories=System;Settings;
StartupNotify=true
EOF

chmod +x "$DESKTOP_DIR/faceunlock.desktop"

# 4. Limpeza ou Instrução Final
echo "4/4. Finalizando configuração..."
echo ""
echo "--- Configuração Concluída com Sucesso! ---"
echo "O Face Unlock agora está instalado em $INSTALL_DIR"
echo "Você já pode encontrar o 'Face Unlock' no seu menu de aplicativos."
echo ""
echo "DICA: Se você estiver no diretório original de desenvolvimento, pode removê-lo se desejar."
