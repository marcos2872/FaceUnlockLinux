import os
import sys

from PySide6.QtCore import Qt, QTimer

# Importação pesada aqui, em um processo separado
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

        layout = QVBoxLayout()
        self.status_label = QLabel(f"Face Unlock: Iniciando para {username}...")
        self.status_label.setStyleSheet("""
            color: white; font-size: 16px; font-weight: bold; 
            background-color: rgba(44, 62, 80, 220);
            padding: 12px; border-radius: 8px; border: 1px solid #34495e;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            "QProgressBar { border: none; background: rgba(0,0,0,50); } "
            "QProgressBar::chunk { background: #3498db; }"
        )

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry((screen.width() - 400) // 2, 30, 400, 80)

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
