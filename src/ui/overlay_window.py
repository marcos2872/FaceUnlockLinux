import os
import sys

# Importação pesada aqui, em um processo separado
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor, QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget


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

        # Layout Principal (Vertical para conter Texto+Ícone e Barra de Progresso)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Layout Superior (Horizontal para Ícone + Texto)
        top_content_layout = QHBoxLayout()
        top_content_layout.setSpacing(15)

        # 1. Adicionar Ícone (face.jpg)
        self.icon_label = QLabel()
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img_path = os.path.join(script_dir, "images", "face.jpg")

        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            # Redimensiona para um tamanho icon-like (ex: 40x40)
            self.icon_label.setPixmap(
                pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        # 2. Texto de Status
        self.status_label = QLabel(f"Face Unlock: {username}")
        self.status_label.setStyleSheet("""
            color: white; font-size: 15px; font-weight: bold; 
        """)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        top_content_layout.addWidget(self.icon_label)
        top_content_layout.addWidget(self.status_label)
        top_content_layout.addStretch()

        # Widget Container para o fundo escuro
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: rgba(44, 62, 80, 230);
                border-radius: 10px;
                border: 1px solid #34495e;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.addLayout(top_content_layout)

        # 3. Barra de Progresso
        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar { border: none; background: rgba(0,0,0,50); border-radius: 2px; } "
            "QProgressBar::chunk { background: #3498db; border-radius: 2px; }"
        )
        container_layout.addWidget(self.progress)

        main_layout.addWidget(self.container)
        self.setLayout(main_layout)

        # --- Lógica de Posicionamento no Monitor Ativo ---
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos) or QApplication.primaryScreen()
        screen_geo = screen.geometry()

        width, height = 420, 100
        x = screen_geo.x() + (screen_geo.width() - width) // 2
        y = screen_geo.y() + 40

        self.setGeometry(x, y, width, height)

    def update_data(self, message, progress_val):
        self.status_label.setText(message)
        self.progress.setValue(progress_val)
        if any(x in message.upper() for x in ["SUCESSO", "OK", "CONCEDIDO"]):
            self.status_label.setStyleSheet(self.status_label.styleSheet() + "color: #2ecc71;")
        elif any(x in message.upper() for x in ["FALHA", "ERRO", "NEGADA"]):
            self.status_label.setStyleSheet(self.status_label.styleSheet() + "color: #e74c3c;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user = sys.argv[1] if len(sys.argv) > 1 else "Usuário"
    window = FeedbackOverlay(user)
    window.show()

    # Timer para fechar automaticamente se o processo pai morrer ou após timeout (15s)
    def check_parent():
        if os.getppid() == 1:  # Órfão
            sys.exit(0)

    # Timer de segurança (auto-destruição em 15s)
    QTimer.singleShot(15000, lambda: sys.exit(0))

    timer = QTimer()
    timer.timeout.connect(check_parent)
    timer.start(1000)

    sys.exit(app.exec())
