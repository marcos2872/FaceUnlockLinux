import os

import cv2
import face_recognition
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog,
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
        self.setWindowTitle(f"Validando: {username}")
        self.setWindowIcon(QIcon(os.path.join(script_dir, "images", "icon.png")))
        self.setFixedSize(660, 650)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.status_label = QLabel("Aguardando detecção...")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0A84FF;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.video_label = QLabel()
        self.video_label.setFixedSize(600, 450)
        self.video_label.setStyleSheet("""
            border: 2px solid #333; 
            border-radius: 20px; 
            background-color: black;
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        self.blink_label = QLabel("Piscadas: 0")
        self.blink_label.setStyleSheet("color: #FF9F0A; font-weight: 600; font-size: 14px;")
        self.blink_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.blink_label)

        self.btn_close = QPushButton("Finalizar Teste")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet(
            "background-color: #3A3A3C; color: white; padding: 12px; font-weight: bold;"
        )
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)

        self.setLayout(layout)
        self.cap = cv2.VideoCapture(0)
        self.blinks = 0
        self.eye_closed = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
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
                self.blink_label.setText(f"Piscadas: {self.blinks}")

            distances = face_recognition.face_distance(self.saved_embeddings, current_encoding)
            min_dist = min(distances) if len(distances) > 0 else 1.0

            if min_dist <= self.threshold:
                color = (88, 209, 48)
                txt = "RECONHECIDO" if self.blinks > 0 else "PISQUE PARA CONFIRMAR"
                self.status_label.setText(f"{txt} ({min_dist:.3f})")
                self.status_label.setStyleSheet(
                    f"color: {'#30D158' if self.blinks > 0 else '#FF9F0A'}; "
                    "font-weight: bold; font-size: 18px;"
                )
                if self.blinks > 0:
                    log_access(self.username, True, "Manual GUI Test Success")
            else:
                color = (255, 69, 58)
                self.status_label.setText(f"NÃO RECONHECIDO ({min_dist:.3f})")
                self.status_label.setStyleSheet(
                    "color: #FF453A; font-weight: bold; font-size: 18px;"
                )

            top, right, bottom, left = face_loc
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        else:
            self.status_label.setText("Nenhum rosto detectado...")
            self.status_label.setStyleSheet("color: #8E8E93; font-weight: bold; font-size: 18px;")

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        q_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(
            QPixmap.fromImage(q_img).scaled(
                600, 450, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
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
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        header = QLabel("Teste de Desbloqueio")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(header)

        # Card Central
        self.card = QWidget()
        self.card.setStyleSheet("""
            QWidget {
                background-color: #282828;
                border-radius: 15px;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(20)

        info_icon = QLabel("📸")
        info_icon.setStyleSheet("font-size: 50px; margin-bottom: 10px;")
        info_icon.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(info_icon)

        instruction = QLabel("Verifique se o reconhecimento está calibrado corretamente.")
        instruction.setStyleSheet("font-size: 16px; color: #A0A0A0;")
        instruction.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(instruction)

        self.btn_test = QPushButton("Iniciar Teste de Câmera")
        self.btn_test.setCursor(Qt.PointingHandCursor)
        self.btn_test.setMinimumHeight(55)
        self.btn_test.setStyleSheet("""
            background-color: #0A84FF; 
            color: white; 
            font-size: 16px; 
            font-weight: bold;
            border-radius: 12px;
        """)
        card_layout.addWidget(self.btn_test)

        layout.addWidget(self.card)
        layout.addStretch()
        self.setLayout(layout)

        self.btn_test.clicked.connect(self.on_test_auth)

    def on_test_auth(self):
        username = self.main_app.get_selected_user()
        if not username:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um usuário na aba 'Usuários'.")
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
