import cv2
import face_recognition
import numpy as np
import time

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

        # Espelhar a imagem horizontalmente (modo espelho)
        frame = cv2.flip(frame, 1)

        # Converter de BGR (OpenCV) para RGB (face_recognition)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detectar localizações de rostos
        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) == 1:
            # Extrair embedding para o rosto detectado
            # encoding é uma lista de encodings, pegamos o primeiro [0]
            encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            embeddings.append(encoding)
            frames_captured += 1
            
            # Feedback visual no terminal (usando \r para atualizar a linha)
            percent = int((frames_captured / num_frames) * 100)
            sys_stdout_write = f"\rProgresso: {percent}% [{frames_captured}/{num_frames}]"
            print(sys_stdout_write, end="", flush=True)
            
            # Desenhar retângulo no rosto para feedback visual (opcional)
            top, right, bottom, left = face_locations[0]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        elif len(face_locations) > 1:
            print("\rAviso: Mais de um rosto detectado. Fique sozinho no frame.", end="", flush=True)
        else:
            print("\rAviso: Nenhum rosto detectado. Aproxime-se.", end="", flush=True)

        # Mostrar preview
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
    Processa um único frame: detecta face e retorna (face_location, encoding).
    Utilizado pela GUI para evitar loops bloqueantes.
    """
    # Converter de BGR (OpenCV) para RGB (face_recognition)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detectar rostos
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if len(face_locations) == 1:
        # Extrair embedding
        encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
        return face_locations[0], encoding
    
    return None, None

def authenticate_user(username, saved_embeddings, threshold=0.5, num_frames=10, show_preview=True):
    """
    Tenta autenticar o usuário capturando alguns frames da webcam.
    saved_embeddings: lista de vetores salvos no cadastro.
    threshold: distância máxima para considerar um match (menor é mais rigoroso).
    show_preview: Se False, não abre janelas do OpenCV (modo PAM).
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return False

    matches_found = 0
    frames_processed = 0
    
    if show_preview:
        print(f"Iniciando autenticação para: {username}...")

    while frames_processed < num_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detectar rostos
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) == 1:
            # Extrair embedding do frame atual
            current_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            
            # Calcular distâncias para todos os embeddings salvos
            distances = face_recognition.face_distance(saved_embeddings, current_encoding)
            
            # Pegamos a menor distância encontrada
            min_dist = min(distances) if len(distances) > 0 else 1.0
            
            if min_dist <= threshold:
                matches_found += 1
                color = (0, 255, 0) # Verde para sucesso
            else:
                color = (0, 0, 255) # Vermelho para falha
                
            if show_preview:
                print(f"Processando: {frames_processed+1}/{num_frames} | Distância: {min_dist:.4f}", end="\r")
                # Desenhar na tela
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        else:
            if show_preview:
                print("Aviso: Olhe para a câmera.", end="\r")

        frames_processed += 1
        
        if show_preview:
            cv2.imshow('Face Unlock - Autenticacao', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if show_preview:
        cv2.destroyAllWindows()
        print("\n")

    # Critério simples: se pelo menos 50% dos frames capturados com rosto deram match
    success_rate = (matches_found / frames_processed) if frames_processed > 0 else 0
    return success_rate >= 0.5
