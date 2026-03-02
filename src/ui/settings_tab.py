import os

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import save_config
from logger import get_last_logs
from system_integration import check_integration, update_integration


class LogDialog(QDialog):
    def __init__(self, script_dir, parent=None):
        super().__init__(parent)
        self.script_dir = script_dir
        self.setWindowTitle("Logs de Acesso")
        self.setWindowIcon(QIcon(os.path.join(script_dir, "images", "icon.png")))
        self.setFixedSize(700, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            QTextEdit {
                font-family: 'JetBrains Mono', 'Fira Code', monospace; 
                background-color: #1E1E1E; 
                color: #30D158;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.text_area)

        btn_close = QPushButton("Fechar")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

        self.refresh_logs()
        self.setLayout(layout)

    def refresh_logs(self):
        logs = get_last_logs()
        self.text_area.setText("".join(logs))


class SettingsTab(QWidget):
    def __init__(self, script_dir, parent=None):
        super().__init__(parent)
        self.script_dir = script_dir
        self.main_app = parent

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        header = QLabel("Integração & Sistema")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(header)

        # --- CARD 1: INTEGRAÇÃO PAM ---
        card_pam = QWidget()
        card_pam.setStyleSheet("background-color: #282828; border-radius: 15px;")
        pam_layout = QVBoxLayout(card_pam)
        pam_layout.setContentsMargins(20, 20, 20, 20)
        pam_layout.setSpacing(15)

        self.selected_user_label = QLabel("Selecione um usuário para configurar")
        self.selected_user_label.setStyleSheet("color: #FF9F0A; font-weight: bold;")
        pam_layout.addWidget(self.selected_user_label)

        self.check_sudo = QCheckBox("Habilitar para 'Sudo' (Terminal)")
        self.check_lock = QCheckBox("Habilitar para 'Lock Screen' (Bloqueio)")
        self.check_login = QCheckBox("Habilitar para 'Login' (SDDM)")
        self.check_polkit = QCheckBox("Habilitar para 'Ações de Admin' (Polkit)")

        pam_layout.addWidget(self.check_sudo)
        pam_layout.addWidget(self.check_lock)
        pam_layout.addWidget(self.check_login)
        pam_layout.addWidget(self.check_polkit)

        self.btn_apply = QPushButton("Aplicar Configurações de Sistema")
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setMinimumHeight(45)
        self.btn_apply.setStyleSheet("background-color: #0A84FF; color: white; font-weight: bold;")
        self.btn_apply.clicked.connect(self.on_apply_integration)
        pam_layout.addWidget(self.btn_apply)

        layout.addWidget(card_pam)

        # --- CARD 2: SENSIBILIDADE ---
        card_sens = QWidget()
        card_sens.setStyleSheet("background-color: #282828; border-radius: 15px;")
        sens_layout = QVBoxLayout(card_sens)
        sens_layout.setContentsMargins(20, 20, 20, 20)

        sens_title = QLabel("Sensibilidade do Sensor")
        sens_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        sens_layout.addWidget(sens_title)

        sens_desc = QLabel("Defina o quão rigoroso o reconhecimento deve ser.")
        sens_desc.setStyleSheet("color: #8E8E93; margin-bottom: 10px;")
        sens_layout.addWidget(sens_desc)

        form_layout = QFormLayout()
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.2, 0.8)
        self.spin_threshold.setSingleStep(0.01)
        self.spin_threshold.setValue(self.main_app.config["threshold"])
        form_layout.addRow("Limiar (Threshold):", self.spin_threshold)
        sens_layout.addLayout(form_layout)

        btn_save = QPushButton("Salvar Preferências")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.on_save_settings)
        sens_layout.addWidget(btn_save)

        layout.addWidget(card_sens)

        # Botão de Logs (Estilo Secundário)
        self.btn_logs = QPushButton("Ver Histórico de Acessos")
        self.btn_logs.setCursor(Qt.PointingHandCursor)
        self.btn_logs.setMinimumHeight(40)
        self.btn_logs.setStyleSheet("background-color: #3A3A3C; color: #A0A0A0;")
        self.btn_logs.clicked.connect(self.on_view_logs)
        layout.addWidget(self.btn_logs)

        layout.addStretch()
        self.setLayout(layout)
        self.update_integration_checks()

    def on_view_logs(self):
        LogDialog(self.script_dir, self).exec()

    def update_integration_checks(self):
        username = self.main_app.get_selected_user()
        if not username:
            self.selected_user_label.setText("⚠️ Selecione um usuário na aba lateral")
            for cb in [self.check_sudo, self.check_lock, self.check_login, self.check_polkit]:
                cb.setChecked(False)
            return

        self.selected_user_label.setText(f"Configurando para: {username}")
        self.check_sudo.setChecked(check_integration("sudo", username) is True)
        self.check_lock.setChecked(check_integration("lockscreen", username) is True)
        self.check_login.setChecked(check_integration("login", username) is True)
        self.check_polkit.setChecked(check_integration("polkit", username) is True)

    def on_apply_integration(self):
        username = self.main_app.get_selected_user()
        if not username:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário primeiro.")
            return
        if (
            QMessageBox.question(self, "Confirmar", f"Aplicar PAM para '{username}'?")
            == QMessageBox.Yes
        ):
            services = {
                "sudo": self.check_sudo.isChecked(),
                "lockscreen": self.check_lock.isChecked(),
                "login": self.check_login.isChecked(),
                "polkit": self.check_polkit.isChecked(),
            }
            for svc, enable in services.items():
                update_integration(svc, username, enable)
            QMessageBox.information(self, "Sucesso", "Integração atualizada!")

    def on_save_settings(self):
        self.main_app.config["threshold"] = self.spin_threshold.value()
        save_config(self.main_app.config)
        QMessageBox.information(self, "Sucesso", "Preferências salvas!")
