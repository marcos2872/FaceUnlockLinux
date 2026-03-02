import os

import cv2
import face_recognition
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

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
        self.setWindowTitle(f"Testando Reconhecimento: {username}")
        self.setWindowIcon(QIcon(os.path.join(script_dir, "images/icon.png")))
        self.setFixedSize(660, 600)
        layout = QVBoxLayout()
        self.status_label = QLabel("Aguardando detecção...")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #555; background-color: black;")
        layout.addWidget(self.video_label)
        self.blink_label = QLabel("Piscadas detectadas: 0")
        self.blink_label.setStyleSheet("color: #e67e22; font-weight: bold;")
        self.blink_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.blink_label)
        self.btn_close = QPushButton("Fechar")
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
                self.blink_label.setText(f"Piscadas detectadas: {self.blinks}")
            for eye in ["left_eye", "right_eye"]:
                for point in landmarks[eye]:
                    cv2.circle(frame, point, 2, (0, 255, 255), -1)
            distances = face_recognition.face_distance(self.saved_embeddings, current_encoding)
            min_dist = min(distances) if len(distances) > 0 else 1.0
            if min_dist <= self.threshold:
                color = (0, 255, 0)
                txt = "RECONHECIDO" if self.blinks > 0 else "AGUARDANDO PISCADA"
                self.status_label.setText(f"{txt} (Dist: {min_dist:.3f})")
                self.status_label.setStyleSheet(
                    f"color: {'green' if self.blinks > 0 else '#f39c12'}; "
                    "font-weight: bold; font-size: 16px;"
                )
                if self.blinks > 0:
                    log_access(self.username, True, "Manual GUI Test Success")
            else:
                color = (0, 0, 255)
                self.status_label.setText(f"NÃO RECONHECIDO (Dist: {min_dist:.3f})")
                self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
            top, right, bottom, left = face_loc
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        else:
            self.status_label.setText("Nenhum rosto detectado...")
            self.status_label.setStyleSheet("color: gray; font-weight: bold; font-size: 16px;")
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        q_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

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
        layout.addWidget(QLabel("<h2>Teste de Reconhecimento</h2>"))
        layout.addWidget(QLabel("Escolha o usuário na primeira aba e clique abaixo para testar."))
        btn_test = QPushButton("Iniciar Teste de Câmera")
        btn_test.setMinimumHeight(60)
        btn_test.clicked.connect(self.on_test_auth)
        layout.addWidget(btn_test)
        layout.addStretch()
        self.setLayout(layout)

    def on_test_auth(self):
        username = self.main_app.get_selected_user()
        if not username:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário primeiro.")
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
