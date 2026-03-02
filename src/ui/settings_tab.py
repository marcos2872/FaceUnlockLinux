import os

from PySide6.QtGui import QIcon
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
        self.setWindowIcon(QIcon(os.path.join(script_dir, "images/icon.png")))
        self.setFixedSize(600, 400)
        layout = QVBoxLayout()
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(
            "font-family: monospace; background-color: #2c3e50; color: #ecf0f1;"
        )
        layout.addWidget(self.text_area)
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
        layout.addWidget(QLabel("<h2>Integração com o Sistema</h2>"))
        self.selected_user_label = QLabel("<b>Usuário Selecionado:</b> (Selecione na primeira aba)")
        self.selected_user_label.setStyleSheet("color: #e67e22; font-size: 14px;")
        layout.addWidget(self.selected_user_label)
        self.check_sudo = QCheckBox("Habilitar para 'Sudo' (Terminal)")
        self.check_lock = QCheckBox("Habilitar para 'Lock Screen' (Bloqueio de Tela)")
        self.check_login = QCheckBox("Habilitar para 'Login' (SDDM)")
        self.check_polkit = QCheckBox("Habilitar para 'Ações de Administrador' (Polkit)")
        layout.addWidget(self.check_sudo)
        layout.addWidget(self.check_lock)
        layout.addWidget(self.check_login)
        layout.addWidget(self.check_polkit)
        btn_apply_pam = QPushButton("Aplicar Integração de Sistema (Requer Root)")
        btn_apply_pam.setStyleSheet(
            "background-color: #3498db; color: white; font-weight: bold; min-height: 40px;"
        )
        btn_apply_pam.clicked.connect(self.on_apply_integration)
        layout.addWidget(btn_apply_pam)
        btn_view_logs = QPushButton("Visualizar Logs de Acesso")
        btn_view_logs.clicked.connect(self.on_view_logs)
        layout.addWidget(btn_view_logs)
        layout.addWidget(QLabel("<hr>"))
        layout.addWidget(QLabel("<h2>Sensibilidade do Sensor</h2>"))
        layout.addWidget(
            QLabel(
                "<p style='color: #7f8c8d;'>Defina o quão rigoroso o sistema deve ser. <br>"
                "<b>0.2 (Rígido):</b> Máxima segurança, mas pode falhar se a luz não estiver boa.<br>"
                "<b>0.8 (Permissivo):</b> Mais fácil de entrar, mas menos seguro contra fotos.</p>"
            )
        )
        form_layout = QFormLayout()
        self.spin_threshold = QDoubleSpinBox()
        self.spin_threshold.setRange(0.2, 0.8)
        self.spin_threshold.setSingleStep(0.01)
        self.spin_threshold.setValue(self.main_app.config["threshold"])
        form_layout.addRow("Valor Threshold:", self.spin_threshold)
        layout.addLayout(form_layout)
        btn_save_config = QPushButton("Salvar Configurações")
        btn_save_config.clicked.connect(self.on_save_settings)
        layout.addWidget(btn_save_config)
        layout.addStretch()
        self.setLayout(layout)
        self.update_integration_checks()

    def on_view_logs(self):
        LogDialog(self.script_dir, self).exec()

    def update_integration_checks(self):
        username = self.main_app.get_selected_user()
        if not username:
            self.selected_user_label.setText(
                "<b>Usuário Selecionado:</b> (Selecione na primeira aba)"
            )
            self.check_sudo.setChecked(False)
            self.check_lock.setChecked(False)
            self.check_login.setChecked(False)
            self.check_polkit.setChecked(False)
            return

        self.selected_user_label.setText(f"<b>Configurando para:</b> {username}")
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
        QMessageBox.information(self, "Sucesso", "Configurações salvas!")
