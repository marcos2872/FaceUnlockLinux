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

from storage import list_users, delete_user, save_user_data
from core import process_face_frame

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
        
        # Display de Vídeo
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #555; background-color: black;")
        layout.addWidget(self.video_label)
        
        # Barra de Progresso
        self.progress = QProgressBar()
        self.progress.setRange(0, 30)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        
        # Lógica de Captura
        self.cap = cv2.VideoCapture(0)
        self.embeddings = []
        self.max_frames = 30
        
        # Timer para o loop de vídeo (~30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)
        
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # Espelhar
        frame = cv2.flip(frame, 1)
        
        # Processar face
        face_loc, encoding = process_face_frame(frame)
        
        if face_loc is not None:
            # Desenhar retângulo no rosto
            top, right, bottom, left = face_loc
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Adicionar embedding e atualizar progresso
            self.embeddings.append(encoding)
            self.progress.setValue(len(self.embeddings))
            
            if len(self.embeddings) >= self.max_frames:
                self.finalize_enrolment()

        # Converter BGR para RGB para o Qt
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def finalize_enrolment(self):
        self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        
        # Salvar no disco
        save_user_data(self.username, self.embeddings)
        self.accept()

    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)

class FaceUnlockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Unlock - Painel de Controle")
        self.resize(800, 600)

        # Widget Central com Abas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Adicionar as Abas
        self.tabs.addTab(self.create_faces_tab(), "Gerenciar Faces")
        self.tabs.addTab(self.create_test_tab(), "Testar Desbloqueio")
        self.tabs.addTab(self.create_settings_tab(), "Configurações")

    def create_faces_tab(self):
        """Aba para listar, adicionar e remover usuários."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<h2>Usuários Cadastrados</h2>"))
        
        self.user_list = QListWidget()
        self.refresh_user_list()
        layout.addWidget(self.user_list)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Cadastrar Novo Rosto")
        btn_remove = QPushButton("Remover Selecionado")
        
        btn_add.clicked.connect(self.on_add_user)
        btn_remove.clicked.connect(self.on_remove_user)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        return widget

    def on_add_user(self):
        """Solicita um nome e inicia o cadastro (Task 15)."""
        username, ok = QInputDialog.getText(self, "Novo Usuário", "Digite o nome para o cadastro:")
        if ok and username:
            dialog = EnrollmentDialog(username, self)
            if dialog.exec():
                QMessageBox.information(self, "Sucesso", f"Usuário '{username}' cadastrado com sucesso!")
                self.refresh_user_list()

    def on_remove_user(self):
        """Remove o usuário selecionado após confirmação."""
        current_item = self.user_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário para remover.")
            return
            
        username = current_item.text()
        if username == "Nenhum usuário cadastrado.":
            return

        confirm = QMessageBox.question(self, "Confirmar Remoção", 
                                     f"Tem certeza que deseja remover os dados faciais de '{username}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            if delete_user(username):
                QMessageBox.information(self, "Sucesso", f"Usuário '{username}' removido.")
                self.refresh_user_list()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível remover o usuário.")

    def create_test_tab(self):
        """Aba para testar a autenticação facial."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Teste de Reconhecimento</h2>"))
        layout.addWidget(QLabel("Clique no botão abaixo para testar o reconhecimento facial."))
        
        btn_test = QPushButton("Iniciar Teste")
        btn_test.setMinimumHeight(50)
        layout.addWidget(btn_test)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_settings_tab(self):
        """Aba para configurações do sistema (threshold, caminhos)."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Configurações do Sistema</h2>"))
        layout.addWidget(QLabel("Opções de sensibilidade e integração com PAM aparecerão aqui."))
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def refresh_user_list(self):
        """Atualiza a lista de usuários na interface."""
        self.user_list.clear()
        users = list_users()
        if users:
            self.user_list.addItems(users)
        else:
            self.user_list.addItem("Nenhum usuário cadastrado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceUnlockApp()
    window.show()
    sys.exit(app.exec())
