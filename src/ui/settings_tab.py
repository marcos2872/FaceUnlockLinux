import os

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
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
                background-color: #1b1e20; 
                color: #27ae60;
                border: 1px solid #4d5052;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.text_area)

        btn_close = QPushButton("Fechar")
        btn_close.setObjectName("action_btn")
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
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("Configuração de Sistema")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #eff0f1;")
        layout.addWidget(header)

        # --- SEÇÃO 1: PAM ---
        self.card_pam = QFrame()
        self.card_pam.setObjectName("section_card")
        pam_layout = QVBoxLayout(self.card_pam)
        pam_layout.setContentsMargins(20, 20, 20, 20)
        pam_layout.setSpacing(12)

        pam_title = QLabel("Integração PAM / Polkit")
        pam_title.setStyleSheet("font-weight: bold; color: #3daee9;")
        pam_layout.addWidget(pam_title)

        self.selected_user_label = QLabel("Aguardando seleção de usuário...")
        self.selected_user_label.setStyleSheet("color: #fdbc4b;")
        pam_layout.addWidget(self.selected_user_label)

        self.check_sudo = QCheckBox("Habilitar Face Unlock para comandos 'Sudo'")
        self.check_lock = QCheckBox("Habilitar para Tela de Bloqueio (KDE Lock)")
        self.check_login = QCheckBox("Habilitar para Login do Sistema (SDDM)")
        self.check_polkit = QCheckBox("Habilitar para Ações Administrativas (Polkit)")

        pam_layout.addWidget(self.check_sudo)
        pam_layout.addWidget(self.check_lock)
        pam_layout.addWidget(self.check_login)
        pam_layout.addWidget(self.check_polkit)

        self.btn_apply = QPushButton("Sincronizar com o Sistema")
        self.btn_apply.setObjectName("primary_action")
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setMinimumHeight(40)
        self.btn_apply.clicked.connect(self.on_apply_integration)
        pam_layout.addWidget(self.btn_apply)

        layout.addWidget(self.card_pam)

        # --- SEÇÃO 2: SENSIBILIDADE ---
        self.card_sens = QFrame()
        self.card_sens.setObjectName("section_card")
        sens_layout = QVBoxLayout(self.card_sens)
        sens_layout.setContentsMargins(20, 20, 20, 20)

        sens_title = QLabel("Calibragem do Sensor")
        sens_title.setStyleSheet("font-weight: bold; color: #eff0f1;")
        sens_layout.addWidget(sens_title)

        sens_legend = QLabel(
            "<b>0.2 (Rígido):</b> Máxima segurança, exige iluminação perfeita.<br>"
            "<b>0.8 (Permissivo):</b> Acesso mais fácil, menos rigoroso."
        )
        sens_legend.setStyleSheet("font-size: 11px; color: #7f8c8d; margin-bottom: 10px;")
        sens_layout.addWidget(sens_legend)

        form_layout = QFormLayout()
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.2, 0.8)
        self.spin_threshold.setSingleStep(0.01)
        self.spin_threshold.setValue(self.main_app.config["threshold"])
        form_layout.addRow("Sensibilidade (Threshold):", self.spin_threshold)
        sens_layout.addLayout(form_layout)

        btn_save = QPushButton("Salvar Calibragem")
        btn_save.setObjectName("action_btn")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.on_save_settings)
        sens_layout.addWidget(btn_save)

        layout.addWidget(self.card_sens)

        # Botão de Logs
        self.btn_logs = QPushButton("Ver Auditoria de Acessos")
        self.btn_logs.setObjectName("action_btn")
        self.btn_logs.setCursor(Qt.PointingHandCursor)
        self.btn_logs.setFixedHeight(35)
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
            self.selected_user_label.setText("⚠️ Selecione um usuário na lista")
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
            QMessageBox.question(
                self, "Confirmar Alterações", f"Aplicar regras de sistema para '{username}'?"
            )
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
            QMessageBox.information(self, "Sucesso", "Configurações sincronizadas!")

    def on_save_settings(self):
        self.main_app.config["threshold"] = self.spin_threshold.value()
        save_config(self.main_app.config)
        QMessageBox.information(self, "Sucesso", "Calibragem salva!")
