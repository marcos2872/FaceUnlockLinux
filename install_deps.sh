#!/bin/bash

# Script de Instalação de Dependências do Face Unlock (Fedora KDE)
echo "--- Instalando Dependências do Face Unlock ---"

# 1. Instalar dependências de sistema
echo "1/3. Instalando dependências do sistema (Requer sudo)..."
sudo dnf install -y cmake gcc-c++ make python3-devel openblas-devel libX11-devel gtk3-devel

# 2. Criar ambiente virtual
echo "2/3. Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install numpy opencv-python PySide6 ruff pre-commit

# 3. Instalar bibliotecas de IA (Compilando dlib)
echo "3/3. Instalando face-recognition (Compilando dlib, isso pode demorar)..."
pip install face-recognition
pip install git+https://github.com/ageitgey/face_recognition_models.git

# 4. Aplicar Patch de compatibilidade (Python 3.14)
echo "Finalizando: Aplicando patch de compatibilidade..."
PKG_DIR=$(find ./venv -name "face_recognition_models" -type d | head -n 1)
cat <<EOF > $PKG_DIR/__init__.py
import os
def pose_predictor_model_location(): return os.path.join(os.path.dirname(__file__), "models", "shape_predictor_68_face_landmarks.dat")
def pose_predictor_five_point_model_location(): return os.path.join(os.path.dirname(__file__), "models", "shape_predictor_5_face_landmarks.dat")
def face_recognition_model_location(): return os.path.join(os.path.dirname(__file__), "models", "dlib_face_recognition_resnet_model_v1.dat")
def cnn_face_detector_model_location(): return os.path.join(os.path.dirname(__file__), "models", "mmod_human_face_detector.dat")
EOF

echo "--- Dependências Instaladas com Sucesso! ---"
echo "Agora você pode rodar: ./setup_app.sh para configurar o aplicativo."
