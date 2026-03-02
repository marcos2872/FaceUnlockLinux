import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

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
        self.setWindowTitle("Face Unlock")
        self.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "images/icon.png")))
        self.resize(1000, 700)

        # Widget Central e Layout Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sidebar (Lateral)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 30, 15, 20)
        self.sidebar_layout.setSpacing(10)

        # Logo/Titulo na Sidebar
        title = QLabel("Face Unlock")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin-bottom: 20px; color: white;"
        )
        self.sidebar_layout.addWidget(title)

        # Botões da Sidebar
        self.btn_faces = self.create_nav_btn("Usuários", 0)
        self.btn_test = self.create_nav_btn("Teste de Câmera", 1)
        self.btn_settings = self.create_nav_btn("Configurações", 2)

        self.sidebar_layout.addStretch()

        # 2. Área de Conteúdo (Direita)
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")

        # Inicializar Componentes (Abas originais)
        self.faces_tab = FacesTab(SCRIPT_DIR, self)
        self.test_tab = TestTab(SCRIPT_DIR, self)
        self.settings_tab = SettingsTab(SCRIPT_DIR, self)

        self.content_area.addWidget(self.faces_tab)
        self.content_area.addWidget(self.test_tab)
        self.content_area.addWidget(self.settings_tab)

        # Adicionar ao Layout Principal
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)

        # Selecionar a primeira tela por padrão
        self.switch_page(0)

    def create_nav_btn(self, text, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_page(index))
        self.sidebar_layout.addWidget(btn)
        return btn

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)

        # Atualizar estado visual dos botões
        btns = [self.btn_faces, self.btn_test, self.btn_settings]
        for i, btn in enumerate(btns):
            btn.setChecked(i == index)
            # No modo Sidebar, podemos usar classes dinâmicas para o estilo
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def get_selected_user(self):
        return self.faces_tab.get_selected_user()

    def update_integration_checks(self):
        self.settings_tab.update_integration_checks()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # --- Apple Crystal Dark Theme ---
    apple_dark = """
        QMainWindow {
            background-color: #1E1E1E;
        }
        
        QWidget#sidebar {
            background-color: #252525;
            border-right: 1px solid #333;
        }
        
        QWidget#content_area {
            background-color: #1E1E1E;
        }

        QPushButton {
            background-color: transparent;
            color: #B0B0B0;
            border-radius: 8px;
            text-align: left;
            padding-left: 15px;
            font-size: 14px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.05);
            color: white;
        }
        
        QPushButton[active="true"] {
            background-color: #0A84FF;
            color: white;
            font-weight: bold;
        }

        /* Estilos para os Tabs internos (agora cards) */
        h2 {
            color: white;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        QLabel {
            color: #A0A0A0;
        }

        QListWidget {
            background-color: #282828;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 5px;
            color: white;
            outline: none;
        }
        
        QListWidget::item {
            padding: 10px;
            border-radius: 8px;
        }
        
        QListWidget::item:selected {
            background-color: #3A3A3C;
            color: #0A84FF;
        }

        QDoubleSpinBox, QCheckBox, QTextEdit {
            background-color: #282828;
            border: 1px solid #333;
            border-radius: 8px;
            color: white;
            padding: 8px;
        }
        
        QPushButton#action_btn { /* Para botões principais de ação */
            background-color: #3A3A3C;
            text-align: center;
            padding: 10px;
            color: white;
        }
        
        QPushButton#action_btn:hover {
            background-color: #48484A;
        }
    """
    app.setStyleSheet(apple_dark)
    app.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "images/icon.png")))

    window = FaceUnlockApp()
    window.show()
    sys.exit(app.exec())
