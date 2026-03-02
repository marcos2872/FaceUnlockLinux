import cv2
import face_recognition
import numpy as np
import time
import sys
import os

# Adicionar src ao path para importar liveness
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
from liveness import check_blink

def capture_embeddings(username, num_frames=30):
    """
    Captura N frames da webcam, detecta o rosto e extrai os embeddings.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return None

    embeddings = []
    frames_captured = 0
    
    print(f"Iniciando cadastro para o usuário: {username}")
    print("Olhe para a câmera e mova levemente o rosto...")

    while frames_captured < num_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) == 1:
            encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            embeddings.append(encoding)
            frames_captured += 1
            
            percent = int((frames_captured / num_frames) * 100)
            sys_stdout_write = f"\rProgresso: {percent}% [{frames_captured}/{num_frames}]"
            print(sys_stdout_write, end="", flush=True)
            
            top, right, bottom, left = face_locations[0]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        elif len(face_locations) > 1:
            print("\rAviso: Mais de um rosto detectado. Fique sozinho no frame.", end="", flush=True)
        else:
            print("\rAviso: Nenhum rosto detectado. Aproxime-se.", end="", flush=True)

        cv2.imshow('Face Unlock - Cadastro', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\nCadastro cancelado pelo usuário.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n")
    return embeddings

def process_face_frame(frame):
    """
    Processa um único frame para a GUI.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    if len(face_locations) == 1:
        encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        # Pegar também os marcos faciais (opcional para a GUI)
        landmarks = face_recognition.face_landmarks(rgb_frame, face_locations)
        return face_locations[0], encoding, (landmarks[0] if landmarks else None)
    return None, None, None

def authenticate_user(username, saved_embeddings, threshold=0.5, num_frames=15, show_preview=True):
    """
    Tenta autenticar o usuário com Liveness Detection (piscada).
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return False

    matches_found = 0
    frames_processed = 0
    blinks_detected = 0
    eye_closed = False
    
    if show_preview:
        print(f"Iniciando autenticação para: {username}...")
        print("Dica: Pisque os olhos para confirmar presença física.")

    # Aumentamos um pouco o tempo total para dar tempo de piscar
    max_frames = num_frames * 2 if show_preview else num_frames + 10

    while frames_processed < max_frames:
        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Obter marcos e localizações
        face_landmarks_list = face_recognition.face_landmarks(rgb_frame)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) == 1 and len(face_landmarks_list) == 1:
            landmarks = face_landmarks_list[0]
            
            # 1. Verificar piscada
            is_blinking = check_blink(landmarks)
            if is_blinking:
                eye_closed = True
            elif not is_blinking and eye_closed:
                blinks_detected += 1
                eye_closed = False
                if show_preview: print(f"\n[OK] Piscada {blinks_detected} detectada!")

            # 2. Verificar similaridade
            current_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            distances = face_recognition.face_distance(saved_embeddings, current_encoding)
            min_dist = min(distances) if len(distances) > 0 else 1.0
            
            if min_dist <= threshold:
                matches_found += 1
                color = (0, 255, 0) # Verde se reconhecido
            else:
                color = (0, 0, 255) # Vermelho se não
                
            if show_preview:
                status = f"Reconhecimento: {matches_found} | Piscadas: {blinks_detected} | Dist: {min_dist:.4f}"
                print(f"\r{status}", end="\r")
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        frames_processed += 1
        if show_preview:
            cv2.imshow('Face Unlock - Autenticacao', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            
        # Critério de saída antecipada: Se já temos matches suficientes e piscada detectada
        if matches_found >= num_frames // 2 and blinks_detected >= 1:
            break

    cap.release()
    if show_preview: cv2.destroyAllWindows(); print("\n")

    # Resultados Finais
    success_rate = (matches_found / frames_processed) if frames_processed > 0 else 0
    is_live = blinks_detected > 0
    
    if show_preview:
        if success_rate >= 0.4 and not is_live:
            print("[Aviso] Usuário reconhecido, mas NENHUMA PISCADA detectada. Autenticação negada por segurança.")
        elif success_rate < 0.4:
            print("[Falha] Usuário não reconhecido.")

    return success_rate >= 0.4 and is_live
