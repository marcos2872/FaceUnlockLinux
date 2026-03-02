import sys

import cv2


def main():
    print("Abrindo webcam... Pressione 'q' para sair.")

    # Tenta abrir a câmera padrão (index 0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        return

    while True:
        # Captura frame por frame
        ret, frame = cap.read()

        if not ret:
            print("Erro ao receber frame. Saindo...")
            break

        # Espelhar a imagem horizontalmente (modo espelho)
        frame = cv2.flip(frame, 1)

        # Mostra o frame em uma janela
        # Mostra o frame em uma janela
        cv2.imshow("Face Unlock - Teste de Camera", frame)

        # Se pressionar 'q', sai do loop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Limpeza
    cap.release()
    cv2.destroyAllWindows()
    print("Teste finalizado.")


if __name__ == "__main__":
    main()
