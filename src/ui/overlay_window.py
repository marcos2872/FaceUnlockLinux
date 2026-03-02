import os
import sys

# Importação pesada aqui, em um processo separado
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QProgressBar, QVBoxLayout, QWidget


class FeedbackOverlay(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # Layout Principal (Vertical para conter o Card e a Barra)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Widget Container (O Card)
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: rgba(44, 62, 80, 230);
                border-radius: 15px;
                border: 1px solid #34495e;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 15)
        container_layout.setSpacing(15)

        # 1. Ícone Centralizado (face.png)
        self.icon_label = QLabel()
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img_path = os.path.join(script_dir, "images", "face.png")

        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.icon_label.setPixmap(
                pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        self.icon_label.setAlignment(Qt.AlignCenter)

        # 2. Texto de Status Abaixo da Imagem
        self.status_label = QLabel(f"Autenticando {username}...")
        self.status_label.setStyleSheet("""
            color: white; font-size: 14px; font-weight: bold;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)

        container_layout.addWidget(self.icon_label)
        container_layout.addWidget(self.status_label)

        # 3. Barra de Progresso Sutil no Fundo do Card
        self.progress = QProgressBar()
        self.progress.setFixedHeight(3)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar { border: none; background: rgba(0,0,0,30); border-radius: 1px; } "
            "QProgressBar::chunk { background: #3498db; }"
        )
        container_layout.addWidget(self.progress)

        main_layout.addWidget(self.container)
        self.setLayout(main_layout)

        # --- Lógica de Posicionamento ---
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos) or QApplication.primaryScreen()
        screen_geo = screen.geometry()

        # Janela um pouco mais alta para o layout vertical
        width, height = 300, 180
        x = screen_geo.x() + (screen_geo.width() - width) // 2
        y = screen_geo.y() + 50

        self.setGeometry(x, y, width, height)

    def update_data(self, message, progress_val):
        self.status_label.setText(message)
        self.progress.setValue(progress_val)
        if any(x in message.upper() for x in ["SUCESSO", "OK", "CONCEDIDO"]):
            self.status_label.setStyleSheet("color: #2ecc71; font-size: 14px; font-weight: bold;")
        elif any(x in message.upper() for x in ["FALHA", "ERRO", "NEGADA"]):
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user = sys.argv[1] if len(sys.argv) > 1 else "Usuário"
    window = FeedbackOverlay(user)
    window.show()

    def check_parent():
        if os.getppid() == 1:
            sys.exit(0)

    QTimer.singleShot(15000, lambda: sys.exit(0))
    timer = QTimer()
    timer.timeout.connect(check_parent)
    timer.start(1000)

    sys.exit(app.exec())
