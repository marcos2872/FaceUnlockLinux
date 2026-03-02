import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, 
                             QWidget, QVBoxLayout, QLabel, QPushButton,
                             QListWidget, QHBoxLayout, QMessageBox, QInputDialog,
                             QDialog, QProgressBar, QDoubleSpinBox, QFormLayout, QCheckBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

# Adicionar src ao path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, 'src'))

from storage import list_users, delete_user, save_user_data, load_user_data, BASE_DIR
from core import process_face_frame
from config import load_config, save_config
from system_integration import check_integration, update_integration
from liveness import check_blink
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
        # Fix: Unpack 3 values
        face_loc, encoding, landmarks = process_face_frame(frame)
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
        if not ret: return
        frame = cv2.flip(frame, 1)
        # Fix: Unpack 3 values
        face_loc, current_encoding, landmarks = process_face_frame(frame)
        
        if face_loc is not None and landmarks is not None:
            # 1. Verificar piscada
            is_blinking = check_blink(landmarks)
            if is_blinking:
                self.eye_closed = True
            elif not is_blinking and self.eye_closed:
                self.blinks += 1
                self.eye_closed = False
                self.blink_label.setText(f"Piscadas detectadas: {self.blinks}")
            
            # 2. Desenhar marcos dos olhos para feedback visual
            for eye in ['left_eye', 'right_eye']:
                for point in landmarks[eye]:
                    cv2.circle(frame, point, 2, (0, 255, 255), -1)

            # 3. Calcular similaridade
            distances = face_recognition.face_distance(self.saved_embeddings, current_encoding)
            min_dist = min(distances) if len(distances) > 0 else 1.0
            
            if min_dist <= self.threshold:
                color = (0, 255, 0)
                txt = "RECONHECIDO" if self.blinks > 0 else "AGUARDANDO PISCADA"
                self.status_label.setText(f"{txt} (Dist: {min_dist:.3f})")
                self.status_label.setStyleSheet(f"color: {'green' if self.blinks > 0 else '#f39c12'}; font-weight: bold; font-size: 16px;")
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
        if hasattr(self, 'cap') and self.cap.isOpened(): self.cap.release()
        super().closeEvent(event)

class FaceUnlockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("Face Unlock - Painel de Controle")
        self.resize(800, 700)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.addTab(self.create_faces_tab(), "Gerenciar Faces")
        self.tabs.addTab(self.create_test_tab(), "Testar Desbloqueio")
        self.tabs.addTab(self.create_settings_tab(), "Integração & Sistema")

    def create_faces_tab(self):
        widget = QWidget(); layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Usuários Cadastrados</h2>"))
        self.user_list = QListWidget()
        self.refresh_user_list()
        self.user_list.itemClicked.connect(self.on_user_selected)
        layout.addWidget(self.user_list)
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Cadastrar Novo Rosto")
        btn_remove = QPushButton("Remover Selecionado")
        btn_add.clicked.connect(self.on_add_user)
        btn_remove.clicked.connect(self.on_remove_user)
        btn_layout.addWidget(btn_add); btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout); widget.setLayout(layout)
        return widget

    def on_user_selected(self, item):
        self.update_integration_checks()

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
            dialog = AuthenticationDialog(username, embeddings, threshold=self.config["threshold"], parent=self)
            dialog.exec()

    def create_settings_tab(self):
        widget = QWidget(); layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Integração com o Sistema</h2>"))
        
        self.selected_user_label = QLabel("<b>Usuário Selecionado:</b> (Selecione na primeira aba)")
        self.selected_user_label.setStyleSheet("color: #e67e22; font-size: 14px;")
        layout.addWidget(self.selected_user_label)
        
        layout.addWidget(QLabel("Selecione onde o Face Unlock deve ser ativado:"))
        self.check_sudo = QCheckBox("Habilitar para 'Sudo' (Terminal)")
        self.check_lock = QCheckBox("Habilitar para 'Lock Screen' (Bloqueio de Tela)")
        self.check_login = QCheckBox("Habilitar para 'Login' (SDDM)")
        
        layout.addWidget(self.check_sudo)
        layout.addWidget(self.check_lock)
        layout.addWidget(self.check_login)
        
        btn_apply_pam = QPushButton("Aplicar Integração de Sistema (Requer Root)")
        btn_apply_pam.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; min-height: 40px;")
        btn_apply_pam.clicked.connect(self.on_apply_integration)
        layout.addWidget(btn_apply_pam)
        
        layout.addWidget(QLabel("<hr>"))
        layout.addWidget(QLabel("<h2>Sensibilidade do Sensor</h2>"))
        
        form_layout = QFormLayout()
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.2, 0.8)
        self.spin_threshold.setSingleStep(0.01)
        self.spin_threshold.setValue(self.config["threshold"])
        form_layout.addRow("Valor Threshold:", self.spin_threshold)
        layout.addLayout(form_layout)
        
        legend = QLabel(
            "<b>Legenda da Sensibilidade:</b><br>"
            "🔹 <b>0.40 ou menor:</b> Máxima Segurança (Rigoroso, evita sósias).<br>"
            "🔸 <b>0.50 (Padrão):</b> Equilíbrio ideal entre segurança e velocidade.<br>"
            "🔹 <b>0.60 ou maior:</b> Mais Flexível (Rápido, mas menos seguro)."
        )
        legend.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px; color: #333;")
        layout.addWidget(legend)
        
        btn_save_config = QPushButton("Salvar Configurações de Sensibilidade")
        btn_save_config.clicked.connect(self.on_save_settings)
        layout.addWidget(btn_save_config)
        
        layout.addWidget(QLabel(f"<b>Diretório de Dados:</b> {BASE_DIR}"))
        layout.addStretch(); widget.setLayout(layout)
        
        self.update_integration_checks()
        return widget

    def update_integration_checks(self):
        item = self.user_list.currentItem()
        if not item or item.text() == "Nenhum usuário cadastrado.":
            self.selected_user_label.setText("<b>Usuário Selecionado:</b> (Selecione na aba 'Gerenciar Faces')")
            return
        
        username = item.text()
        self.selected_user_label.setText(f"<b>Configurando para:</b> {username}")
        self.check_sudo.setChecked(check_integration("sudo", username) == True)
        self.check_lock.setChecked(check_integration("lockscreen", username) == True)
        self.check_login.setChecked(check_integration("login", username) == True)

    def on_apply_integration(self):
        item = self.user_list.currentItem()
        if not item or item.text() == "Nenhum usuário cadastrado.":
            QMessageBox.warning(self, "Aviso", "Selecione um usuário para configurar a integração.")
            return
        
        username = item.text()
        msg = (f"Deseja aplicar as configurações de PAM para o usuário <b>'{username}'</b>?\n\n"
               "Os arquivos em /etc/pam.d/ serão atualizados.")
        
        if QMessageBox.question(self, "Confirmar Integração", msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            services = {
                "sudo": self.check_sudo.isChecked(),
                "lockscreen": self.check_lock.isChecked(),
                "login": self.check_login.isChecked()
            }
            
            errors = []
            for svc, enable in services.items():
                success, error = update_integration(svc, username, enable)
                if not success:
                    errors.append(f"{svc}: {error}")
            
            if errors:
                QMessageBox.critical(self, "Erro", "Falha ao atualizar PAM:\n" + "\n".join(errors) +
                                   "\n\nCertifique-se de estar rodando com sudo.")
            else:
                QMessageBox.information(self, "Sucesso", "Integração de sistema atualizada!")

    def on_save_settings(self):
        self.config["threshold"] = self.spin_threshold.value()
        save_config(self.config)
        QMessageBox.information(self, "Sucesso", "Configurações de sensibilidade salvas!")

    def refresh_user_list(self):
        self.user_list.clear()
        users = list_users()
        if users: self.user_list.addItems(users)
        else: self.user_list.addItem("Nenhum usuário cadastrado.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceUnlockApp(); window.show(); sys.exit(app.exec())
