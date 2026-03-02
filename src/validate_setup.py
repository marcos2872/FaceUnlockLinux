import cv2
import face_recognition
import numpy as np
import sys

def validate():
    print(f"--- Validando Setup (Fedora KDE) ---")
    print(f"OpenCV: {cv2.__version__}")
    
    # 1. Testar acesso à câmera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("AVISO: Não foi possível acessar a webcam (index 0).")
    else:
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("ERRO: Falha ao ler frame da webcam.")
        else:
            print("Câmera acessada com sucesso.")

    # 2. Testar processamento facial
    try:
        # Criar uma imagem preta simulando um frame para testar a lib
        fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        # Tenta detectar faces numa imagem vazia (deve retornar lista vazia)
        face_locations = face_recognition.face_locations(fake_frame)
        print(f"Biblioteca face_recognition carregada. Teste de detecção funcional.")
    except Exception as e:
        print(f"ERRO no face_recognition: {e}")
        return False

    print("--- Setup Validado com Sucesso ---")
    return True

if __name__ == "__main__":
    if not validate():
        sys.exit(1)
