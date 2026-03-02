import numpy as np


def eye_aspect_ratio(eye_landmarks):
    """
    Calcula o Eye Aspect Ratio (EAR) para detectar se o olho está aberto ou fechado.
    """
    # Pontos verticais
    A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])

    # Ponto horizontal
    C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])

    # Calcular EAR
    ear = (A + B) / (2.0 * C)
    return ear


def check_blink(face_landmarks, threshold=0.22):
    """
    Verifica se ambos os olhos estão fechados baseado nos marcos faciais.
    """
    if "left_eye" not in face_landmarks or "right_eye" not in face_landmarks:
        return False

    left_ear = eye_aspect_ratio(np.array(face_landmarks["left_eye"]))
    right_ear = eye_aspect_ratio(np.array(face_landmarks["right_eye"]))

    # Média dos dois olhos
    avg_ear = (left_ear + right_ear) / 2.0

    # Retorna True se o EAR for menor que o threshold (olho fechado)
    return avg_ear < threshold
