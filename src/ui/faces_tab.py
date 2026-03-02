import os

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import process_face_frame
from liveness import check_blink
from storage import delete_user, list_users, save_user_data


class EnrollmentDialog(QDialog):
    def __init__(self, username, script_dir, parent=None):
        super().__init__(parent)
        self.username = username
        self.script_dir = script_dir
        self.setWindowTitle(f"Cadastrando: {username}")
        self.setWindowIcon(QIcon(os.path.join(script_dir, "images", "icon.png")))
        self.setFixedSize(660, 620)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.status_label = QLabel("Olhe para a câmera e PISQUE...")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0A84FF;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.video_label = QLabel()
        self.video_label.setFixedSize(600, 450)
        # Borda arredondada para o feed da câmera
        self.video_label.setStyleSheet("""
            border: 2px solid #333; 
            border-radius: 20px; 
            background-color: black;
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 30)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        self.blink_status = QLabel("Vivacidade: ❌")
        self.blink_status.setStyleSheet("font-weight: 600; color: #FF453A;")
        self.blink_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.blink_status)

        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)
        self.embeddings = []
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
        face_loc, encoding, landmarks = process_face_frame(frame)
        if face_loc is not None and landmarks is not None:
            is_blinking = check_blink(landmarks)
            if is_blinking:
                self.eye_closed = True
            elif not is_blinking and self.eye_closed:
                self.blinks += 1
                self.eye_closed = False
                self.blink_status.setText("Vivacidade: ✅")
                self.blink_status.setStyleSheet("font-weight: 600; color: #30D158;")
                self.status_label.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #30D158;"
                )

            if len(self.embeddings) < 30:
                self.embeddings.append(encoding)
                self.progress.setValue(len(self.embeddings))

            if len(self.embeddings) >= 30 and self.blinks > 0:
                self.finalize_enrolment()

            top, right, bottom, left = face_loc
            color = (88, 209, 48) if self.blinks > 0 else (255, 69, 58)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        q_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)

        # Converter para pixmap e aplicar arredondamento via código se necessário
        # Aqui apenas setamos no label que já tem border-radius no stylesheet
        self.video_label.setPixmap(
            QPixmap.fromImage(q_img).scaled(
                600, 450, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
        )

    def finalize_enrolment(self):
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        save_user_data(self.username, self.embeddings)
        self.accept()

    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)


class FacesTab(QWidget):
    def __init__(self, script_dir, parent=None):
        super().__init__(parent)
        self.script_dir = script_dir
        self.main_app = parent

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        header = QLabel("Gerenciar Usuários")
        header.setObjectName("header")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(header)

        # Card de Conteúdo
        self.card = QWidget()
        self.card.setStyleSheet("""
            QWidget {
                background-color: #282828;
                border-radius: 15px;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        card_layout.addWidget(QLabel("Lista de Acesso"))

        self.user_list = QListWidget()
        self.refresh_user_list()
        self.user_list.itemClicked.connect(self.on_user_selected)
        card_layout.addWidget(self.user_list)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_add = QPushButton("Adicionar Rosto")
        self.btn_add.setObjectName("action_btn")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet(
            "background-color: #0A84FF; color: white; padding: 12px; font-weight: bold;"
        )

        self.btn_remove = QPushButton("Remover Selecionado")
        self.btn_remove.setObjectName("action_btn")
        self.btn_remove.setCursor(Qt.PointingHandCursor)
        self.btn_remove.setStyleSheet("background-color: #3A3A3C; color: #FF453A; padding: 12px;")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        card_layout.addLayout(btn_layout)

        layout.addWidget(self.card)
        layout.addStretch()
        self.setLayout(layout)

        self.btn_add.clicked.connect(self.on_add_user)
        self.btn_remove.clicked.connect(self.on_remove_user)

    def refresh_user_list(self):
        self.user_list.clear()
        users = list_users()
        if users:
            self.user_list.addItems(users)
        else:
            self.user_list.addItem("Nenhum usuário cadastrado.")

    def on_user_selected(self, item):
        if hasattr(self.main_app, "update_integration_checks"):
            self.main_app.update_integration_checks()

    def on_add_user(self):
        username, ok = QInputDialog.getText(self, "Novo Usuário", "Digite o nome para o cadastro:")
        if ok and username:
            dialog = EnrollmentDialog(username, self.script_dir, self)
            if dialog.exec():
                QMessageBox.information(
                    self, "Sucesso", f"Usuário '{username}' cadastrado com sucesso!"
                )
                self.refresh_user_list()

    def on_remove_user(self):
        item = self.user_list.currentItem()
        if not item or item.text() == "Nenhum usuário cadastrado.":
            return
        if (
            QMessageBox.question(self, "Confirmação", f"Deseja remover '{item.text()}'?")
            == QMessageBox.Yes
        ):
            if delete_user(item.text()):
                self.refresh_user_list()

    def get_selected_user(self):
        item = self.user_list.currentItem()
        if not item or item.text() == "Nenhum usuário cadastrado.":
            return None
        return item.text()
