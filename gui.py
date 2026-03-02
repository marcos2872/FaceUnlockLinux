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
        self.setWindowTitle("Face Unlock - Configurações")
        self.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "images/icon.png")))
        self.resize(1100, 750)

        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sidebar (KDE Breeze Style)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 10, 0, 10)
        self.sidebar_layout.setSpacing(2)

        # Titulo da Sidebar
        title_container = QWidget()
        title_container.setFixedHeight(60)
        title_layout = QHBoxLayout(title_container)
        title = QLabel("Face Unlock")
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #eff0f1; padding-left: 15px;"
        )
        title_layout.addWidget(title)
        self.sidebar_layout.addWidget(title_container)

        # Botões da Sidebar com Ícones do Sistema
        self.btn_faces = self.create_nav_btn("Usuários", "user-identity", 0)
        self.btn_test = self.create_nav_btn("Teste de Câmera", "camera-web", 1)
        self.btn_settings = self.create_nav_btn("Integração & Sistema", "preferences-system", 2)

        self.sidebar_layout.addStretch()

        # 2. Área de Conteúdo
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        # Barra de Status Superior (Badge de Usuário)
        self.user_header = QWidget()
        self.user_header.setFixedHeight(50)
        self.user_header.setStyleSheet(
            "background-color: #2a2e32; border-bottom: 1px solid #4d5052;"
        )
        header_layout = QHBoxLayout(self.user_header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        self.user_badge = QLabel("Nenhum usuário")
        self.user_badge.setStyleSheet("""
            QLabel {
                background-color: #3daee9;
                color: white;
                padding: 4px 12px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Usuário Ativo:"))
        header_layout.addWidget(self.user_badge)

        self.content_area = QStackedWidget()
        self.content_area.setObjectName("content_area")

        self.faces_tab = FacesTab(SCRIPT_DIR, self)
        self.test_tab = TestTab(SCRIPT_DIR, self)
        self.settings_tab = SettingsTab(SCRIPT_DIR, self)

        self.content_area.addWidget(self.faces_tab)
        self.content_area.addWidget(self.test_tab)
        self.content_area.addWidget(self.settings_tab)

        self.right_layout.addWidget(self.user_header)
        self.right_layout.addWidget(self.content_area)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.right_container)

        # Agora que tudo está inicializado, fazemos o carregamento inicial da lista
        self.faces_tab.refresh_user_list()
        self.switch_page(0)

    def update_user_badge(self, username):
        if username:
            self.user_badge.setText(username.upper())
            self.user_badge.setStyleSheet(
                "color: #eff0f1; padding: 4px 0px; font-weight: bold; font-size: 13px;"
            )
        else:
            self.user_badge.setText("NENHUM")
            self.user_badge.setStyleSheet(
                "color: #7f8c8d; padding: 4px 0px; font-weight: bold; font-size: 13px;"
            )

    def create_nav_btn(self, text, icon_name, index):
        btn = QPushButton()
        btn.setCheckable(True)
        btn.setFixedHeight(45)
        btn.setCursor(Qt.PointingHandCursor)

        # Layout interno para ícone + texto
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(20, 0, 10, 0)
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setPixmap(QIcon.fromTheme(icon_name).pixmap(22, 22))

        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 13px; background: transparent; color: inherit;")

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()

        btn.clicked.connect(lambda: self.switch_page(index))
        self.sidebar_layout.addWidget(btn)
        return btn

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)
        btns = [self.btn_faces, self.btn_test, self.btn_settings]
        for i, btn in enumerate(btns):
            btn.setChecked(i == index)
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

    # --- KDE Breeze Dark Theme ---
    breeze_dark = """
        QMainWindow {
            background-color: #232629;
        }
        
        QWidget#sidebar {
            background-color: #31363b;
            border-right: 1px solid #4d5052;
        }
        
        QWidget#content_area {
            background-color: #232629;
        }

        QPushButton {
            background-color: transparent;
            color: #eff0f1;
            border: none;
            border-radius: 0px;
            text-align: left;
        }
        
        QPushButton:hover {
            background-color: #454a4e;
            color: #ffffff;
        }
        
        QPushButton[active="true"] {
            background-color: #31363b;
            border-left: 4px solid #7f8c8d;
            color: #ffffff;
            font-weight: bold;
        }

        h2 {
            color: #ffffff;
            font-size: 22px;
            font-weight: 500;
        }
        
        QLabel {
            color: #eff0f1;
        }

        /* Frames para seções (estilo GroupBox) */
        QFrame#section_card {
            background-color: #31363b;
            border: 1px solid #4d5052;
            border-radius: 4px;
        }

        QListWidget {
            background-color: #232629;
            border: 1px solid #4d5052;
            border-radius: 2px;
            color: #eff0f1;
        }
        
        QListWidget::item {
            padding: 8px;
        }
        
        QListWidget::item:selected {
            background-color: #454a4e;
            color: white;
        }

        QDoubleSpinBox, QCheckBox, QTextEdit, QLineEdit {
            background-color: #31363b;
            border: 1px solid #4d5052;
            border-radius: 3px;
            color: #eff0f1;
            padding: 6px;
        }

        QDoubleSpinBox:focus, QLineEdit:focus {
            border: 1px solid #7f8c8d;
        }

        /* Botões de Ação estilo Breeze */
        QPushButton#action_btn {
            background-color: #31363b;
            border: 1px solid #4d5052;
            border-radius: 3px;
            padding: 8px 16px;
            color: #eff0f1;
        }
        
        QPushButton#action_btn:hover {
            border: 1px solid #7f8c8d;
            background-color: #31363b;
        }

        QPushButton#primary_action {
            background-color: #454a4e;
            border: 1px solid #7f8c8d;
            color: white;
            font-weight: bold;
        }
        
        QPushButton#primary_action:hover {
            background-color: #4d5052;
        }
    """
    app.setStyleSheet(breeze_dark)
    app.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "images/icon.png")))

    window = FaceUnlockApp()
    window.show()
    sys.exit(app.exec())
