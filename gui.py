import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                             QWidget, QVBoxLayout, QLabel, QPushButton,
                             QListWidget, QHBoxLayout, QMessageBox, QInputDialog,
                             QDialog, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

# Adicionar src ao path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, 'src'))

from storage import list_users, delete_user, save_user_data, load_user_data
from core import process_face_frame
import face_recognition

class EnrollmentDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle(f"Cadastrando Rosto: {username}")
        self.setFixedSize(660, 580)
        
        layout = QVBoxLayout()
        self.status_label = QLabel(f"Olhe para a câmera e mova levemente o rosto...")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #555; background-color: black;")
        layout.addWidget(self.video_label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 30)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        self.cap = cv2.VideoCapture(0)
        self.embeddings = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        frame = cv2.flip(frame, 1)
        face_loc, encoding = process_face_frame(frame)
        if face_loc is not None:
            top, right, bottom, left = face_loc
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            self.embeddings.append(encoding)
            self.progress.setValue(len(self.embeddings))
            if len(self.embeddings) >= 30: self.finalize_enrolment()
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        q_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def finalize_enrolment(self):
        self.timer.stop()
        if self.cap.isOpened(): self.cap.release()
        save_user_data(self.username, self.embeddings)
        self.accept()

    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, 'cap') and self.cap.isOpened(): self.cap.release()
        super().closeEvent(event)

class AuthenticationDialog(QDialog):
    def __init__(self, username, saved_embeddings, threshold=0.5, parent=None):
        super().__init__(parent)
        self.username = username
        self.saved_embeddings = saved_embeddings
        self.threshold = threshold
        self.setWindowTitle(f"Testando Reconhecimento: {username}")
        self.setFixedSize(660, 580)
        
        layout = QVBoxLayout()
        self.status_label = QLabel("Aguardando detecção...")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #555; background-color: black;")
        layout.addWidget(self.video_label)
        
        self.btn_close = QPushButton("Fechar")
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)
        
        self.setLayout(layout)
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        frame = cv2.flip(frame, 1)
        face_loc, current_encoding = process_face_frame(frame)
        
        if face_loc is not None:
            # Calcular distância
            distances = face_recognition.face_distance(self.saved_embeddings, current_encoding)
            min_dist = min(distances) if len(distances) > 0 else 1.0
            
            if min_dist <= self.threshold:
                color = (0, 255, 0) # Verde
                self.status_label.setText(f"SUCESSO! (Distância: {min_dist:.4f})")
                self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 16px;")
            else:
                color = (0, 0, 255) # Vermelho
                self.status_label.setText(f"NÃO RECONHECIDO (Distância: {min_dist:.4f})")
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
        if hasattr(self, 'cap') and self.cap.isOpened(): self.cap.release()
        super().closeEvent(event)

class FaceUnlockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Unlock - Painel de Controle")
        self.resize(800, 600)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(self.create_faces_tab(), "Gerenciar Faces")
        self.tabs.addTab(self.create_test_tab(), "Testar Desbloqueio")
        self.tabs.addTab(self.create_settings_tab(), "Configurações")

    def create_faces_tab(self):
        widget = QWidget(); layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Usuários Cadastrados</h2>"))
        self.user_list = QListWidget()
        self.refresh_user_list()
        layout.addWidget(self.user_list)
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Cadastrar Novo Rosto")
        btn_remove = QPushButton("Remover Selecionado")
        btn_add.clicked.connect(self.on_add_user)
        btn_remove.clicked.connect(self.on_remove_user)
        btn_layout.addWidget(btn_add); btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout); widget.setLayout(layout)
        return widget

    def on_add_user(self):
        username, ok = QInputDialog.getText(self, "Novo Usuário", "Digite o nome para o cadastro:")
        if ok and username:
            dialog = EnrollmentDialog(username, self)
            if dialog.exec():
                QMessageBox.information(self, "Sucesso", f"Usuário '{username}' cadastrado!")
                self.refresh_user_list()

    def on_remove_user(self):
        item = self.user_list.currentItem()
        if not item: return
        username = item.text()
        if username == "Nenhum usuário cadastrado.": return
        if QMessageBox.question(self, "Confirmação", f"Remover '{username}'?") == QMessageBox.Yes:
            if delete_user(username): self.refresh_user_list()

    def create_test_tab(self):
        widget = QWidget(); layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Teste de Reconhecimento</h2>"))
        layout.addWidget(QLabel("Escolha o usuário na primeira aba e clique abaixo para testar."))
        btn_test = QPushButton("Iniciar Teste de Câmera")
        btn_test.setMinimumHeight(60)
        btn_test.clicked.connect(self.on_test_auth)
        layout.addWidget(btn_test)
        layout.addStretch(); widget.setLayout(layout)
        return widget

    def on_test_auth(self):
        item = self.user_list.currentItem()
        if not item or item.text() == "Nenhum usuário cadastrado.":
            QMessageBox.warning(self, "Aviso", "Selecione um usuário cadastrado na aba 'Gerenciar Faces'.")
            return
        
        username = item.text()
        embeddings, meta = load_user_data(username)
        if embeddings is not None:
            dialog = AuthenticationDialog(username, embeddings, parent=self)
            dialog.exec()

    def create_settings_tab(self):
        widget = QWidget(); layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Configurações do Sistema</h2>"))
        layout.addWidget(QLabel("Sensibilidade (Threshold):"))
        layout.addStretch(); widget.setLayout(layout)
        return widget

    def refresh_user_list(self):
        self.user_list.clear()
        users = list_users()
        if users: self.user_list.addItems(users)
        else: self.user_list.addItem("Nenhum usuário cadastrado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceUnlockApp(); window.show(); sys.exit(app.exec())
