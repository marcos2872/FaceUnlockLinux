import os

import cv2
import face_recognition
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import process_face_frame
from liveness import check_blink
from logger import log_access
from storage import load_user_data


class AuthenticationDialog(QDialog):
    def __init__(self, username, saved_embeddings, script_dir, threshold=0.5, parent=None):
        super().__init__(parent)
        self.username = username
        self.saved_embeddings = saved_embeddings
        self.threshold = threshold
        self.script_dir = script_dir
        self.setWindowTitle(f"Verificar Identidade - {username}")
        self.setWindowIcon(QIcon(os.path.join(script_dir, "images", "icon.png")))
        self.setFixedSize(660, 620)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.status_label = QLabel("Iniciando sensor de câmera...")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3daee9;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.video_frame = QFrame()
        self.video_frame.setObjectName("section_card")
        self.video_frame.setFixedSize(620, 470)
        video_layout = QVBoxLayout(self.video_frame)

        self.video_label = QLabel()
        self.video_label.setFixedSize(600, 450)
        self.video_label.setStyleSheet("background-color: black; border-radius: 2px;")
        self.video_label.setAlignment(Qt.AlignCenter)
        video_layout.addWidget(self.video_label)
        layout.addWidget(self.video_frame)

        self.blink_label = QLabel("Piscadas detectadas: 0")
        self.blink_label.setStyleSheet("color: #fdbc4b; font-weight: bold;")  # Yellow Breeze
        self.blink_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.blink_label)

        self.btn_close = QPushButton("Encerrar Teste")
        self.btn_close.setObjectName("action_btn")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)

        self.setLayout(layout)

        self.cap = None
        self.blinks = 0
        self.eye_closed = False

        # Timer de captura
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Inicialização assíncrona da câmera
        QTimer.singleShot(500, self.init_camera)

    def init_camera(self):
        self.status_label.setText("Conectando ao sensor...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)

        if not self.cap or not self.cap.isOpened():
            QMessageBox.critical(
                self,
                "Erro de Câmera",
                "O sensor de vídeo não responde. Verifique se a câmera está ocupada.",
            )
            self.reject()
            return

        self.status_label.setText("Câmera OK! Verificando rosto...")
        self.timer.start(33)

    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.status_label.setText("Sinal da câmera perdido.")
            self.timer.stop()
            return
        frame = cv2.flip(frame, 1)
        face_loc, current_encoding, landmarks = process_face_frame(frame)
        if face_loc is not None and landmarks is not None:
            is_blinking = check_blink(landmarks)
            if is_blinking:
                self.eye_closed = True
            elif not is_blinking and self.eye_closed:
                self.blinks += 1
                self.eye_closed = False
                self.blink_label.setText(f"Piscadas detectadas: {self.blinks}")

            distances = face_recognition.face_distance(self.saved_embeddings, current_encoding)
            min_dist = min(distances) if len(distances) > 0 else 1.0

            if min_dist <= self.threshold:
                color = (88, 209, 48)
                txt = "IDENTIDADE CONFIRMADA" if self.blinks > 0 else "AGUARDANDO PISCADA"
                self.status_label.setText(f"{txt} (Dist: {min_dist:.3f})")
                self.status_label.setStyleSheet(
                    f"color: {'#27ae60' if self.blinks > 0 else '#fdbc4b'}; font-weight: bold;"
                )
                if self.blinks > 0:
                    log_access(self.username, True, "Manual GUI Test Success")
            else:
                color = (218, 68, 83)
                self.status_label.setText(f"ACESSO NEGADO (Dist: {min_dist:.3f})")
                self.status_label.setStyleSheet("color: #da4453; font-weight: bold;")

            top, right, bottom, left = face_loc
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        else:
            self.status_label.setText("Nenhum rosto detectado...")
            self.status_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        q_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(
            QPixmap.fromImage(q_img).scaled(600, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)


class TestTab(QWidget):
    def __init__(self, script_dir, parent=None):
        super().__init__(parent)
        self.script_dir = script_dir
        self.main_app = parent

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("Diagnóstico de Reconhecimento")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #eff0f1;")
        layout.addWidget(header)

        # Card Central estilo Breeze
        self.card = QFrame()
        self.card.setObjectName("section_card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        instruction = QLabel(
            "Teste a precisão do sensor antes de habilitar as integrações de sistema."
        )
        instruction.setStyleSheet("color: #bdc3c7;")
        instruction.setWordWrap(True)
        card_layout.addWidget(instruction)

        self.btn_test = QPushButton("Iniciar Teste de Câmera")
        self.btn_test.setObjectName("primary_action")
        self.btn_test.setCursor(Qt.PointingHandCursor)
        self.btn_test.setMinimumHeight(45)
        card_layout.addWidget(self.btn_test)

        layout.addWidget(self.card)
        layout.addStretch()
        self.setLayout(layout)

        self.btn_test.clicked.connect(self.on_test_auth)

    def on_test_auth(self):
        username = self.main_app.get_selected_user()
        if not username:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário na lista lateral primeiro.")
            return
        embeddings, meta = load_user_data(username)
        if embeddings is not None:
            AuthenticationDialog(
                username,
                embeddings,
                self.script_dir,
                threshold=self.main_app.config["threshold"],
                parent=self,
            ).exec()
