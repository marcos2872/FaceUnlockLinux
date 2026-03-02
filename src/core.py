import os
import sys

import cv2
import face_recognition

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)
from liveness import check_blink  # noqa: E402


def process_face_frame(frame):
    """
    Processa um único frame para detectar rostos e landmarks.
    Retorna: (face_location, face_encoding, face_landmarks) ou (None, None, None)
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        return None, None, None

    # Pegamos apenas a primeira face detectada
    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
    face_landmarks = face_recognition.face_landmarks(rgb_frame, face_locations)[0]

    return face_locations[0], face_encoding, face_landmarks


def capture_embeddings(username, num_frames=30):
    """
    Captura frames da webcam e extrai embeddings para cadastro.
    Exige que o usuário pisque para garantir vivacidade.
    """
    cap = cv2.VideoCapture(0)
    frames_captured = 0
    blinks_detected = 0
    eye_closed = False
    embeddings = []

    print(f"Iniciando cadastro para: {username}")
    print("Por favor, olhe para a câmera e PISQUE os olhos para validar...")

    while frames_captured < num_frames or blinks_detected == 0:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        face_loc, encoding, landmarks = process_face_frame(frame)

        if face_loc is not None:
            # 1. Verificar piscada
            is_blinking = check_blink(landmarks)
            if is_blinking:
                eye_closed = True
            elif not is_blinking and eye_closed:
                blinks_detected += 1
                eye_closed = False
                print(f"\n[OK] Piscada {blinks_detected} detectada!")

            # 2. Coletar embeddings
            if frames_captured < num_frames:
                embeddings.append(encoding)
                frames_captured += 1
                print(f"\rCapturando: {frames_captured}/{num_frames} frames...", end="\r")

            # Feedback visual no terminal
            top, right, bottom, left = face_loc
            color = (0, 255, 0) if blinks_detected > 0 else (0, 255, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        cv2.imshow("Face Unlock - Cadastro", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if blinks_detected > 0:
        return embeddings
    else:
        print("\n[Erro] Nenhuma piscada detectada. Cadastro cancelado por segurança.")
        return None


def authenticate_user(
    username,
    saved_embeddings,
    threshold=0.5,
    num_frames=15,
    show_preview=True,
    status_callback=None,
):
    """
    Autentica um usuário comparando o frame atual com os embeddings salvos.
    Exige reconhecimento E vivacidade (piscada).
    """
    cap = cv2.VideoCapture(0)
    frames_processed = 0
    matches_found = 0
    blinks_detected = 0
    eye_closed = False
    max_frames = num_frames * 3  # Tenta por até 3x o número de frames solicitados

    is_live = False

    if status_callback:
        status_callback("Face Unlock: Procurando Rosto...", 10)

    while frames_processed < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        face_loc, current_encoding, landmarks = process_face_frame(frame)

        if face_loc is not None:
            # 1. Verificar vivacidade
            is_blinking = check_blink(landmarks)
            if is_blinking:
                eye_closed = True
            elif not is_blinking and eye_closed:
                blinks_detected += 1
                eye_closed = False
                msg = f"Piscada {blinks_detected} detectada!"
                if show_preview:
                    print(f"\n[OK] {msg}")
                if status_callback:
                    status_callback(f"Face Unlock: {msg}", 50)

            # 2. Verificar similaridade
            distances = face_recognition.face_distance(saved_embeddings, current_encoding)
            min_dist = min(distances) if len(distances) > 0 else 1.0

            if min_dist <= threshold:
                matches_found += 1
                color = (0, 255, 0)
                if status_callback and blinks_detected == 0:
                    status_callback("Rosto Reconhecido! PISQUE para confirmar.", 40)
            else:
                color = (0, 0, 255)

            if show_preview:
                status = (
                    f"Reconhecimento: {matches_found} | "
                    f"Piscadas: {blinks_detected} | Dist: {min_dist:.4f}"
                )
                print(f"\r{status}", end="\r")
                top, right, bottom, left = face_loc
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        if show_preview:
            cv2.imshow("Face Unlock - Autenticacao", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Critério de saída antecipada: Se já temos matches suficientes e piscada detectada
        if matches_found >= num_frames // 2 and blinks_detected > 0:
            is_live = True
            break

        frames_processed += 1

    cap.release()
    if show_preview:
        cv2.destroyAllWindows()
        print("\n")

    # Resultados Finais
    success_rate = matches_found / num_frames if num_frames > 0 else 0
    if success_rate >= 0.4 and blinks_detected > 0:
        return True

    if show_preview:
        if success_rate >= 0.4 and not is_live:
            print(
                "[Aviso] Usuário reconhecido, mas NENHUMA PISCADA detectada. "
                "Autenticação negada por segurança."
            )
        elif success_rate < 0.4:
            print("[Falha] Usuário não reconhecido.")

    return False
