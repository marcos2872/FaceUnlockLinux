import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

# Adicionar src ao path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, "src"))
sys.path.append(os.path.join(SCRIPT_DIR, "src", "ui"))

from faces_tab import FacesTab  # noqa: E402
from settings_tab import SettingsTab  # noqa: E402
from test_tab import TestTab  # noqa: E402

from config import load_config  # noqa: E402


class FaceUnlockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("Face Unlock - Painel de Controle")
        self.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "images/icon.png")))
        self.resize(800, 750)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Inicializar Tabs
        self.faces_tab = FacesTab(SCRIPT_DIR, self)
        self.test_tab = TestTab(SCRIPT_DIR, self)
        self.settings_tab = SettingsTab(SCRIPT_DIR, self)

        self.tabs.addTab(self.faces_tab, "Gerenciar Faces")
        self.tabs.addTab(self.test_tab, "Testar Desbloqueio")
        self.tabs.addTab(self.settings_tab, "Integração & Sistema")

    def get_selected_user(self):
        return self.faces_tab.get_selected_user()

    def update_integration_checks(self):
        self.settings_tab.update_integration_checks()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "images/icon.png")))
    window = FaceUnlockApp()
    window.show()
    sys.exit(app.exec())
