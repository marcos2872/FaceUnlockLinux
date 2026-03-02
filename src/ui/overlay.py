import os
import sys


class OverlayApp:
    """Helper para gerenciar o Overlay de forma segura."""

    def __init__(self, username):
        self.available = False
        # Se não houver display, nem tenta carregar o PySide6 (evita crash fatal)
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            return

        try:
            # Importação local para evitar crash no topo do arquivo
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QApplication, QLabel, QProgressBar, QVBoxLayout, QWidget

            # Classe interna para a janela
            class FeedbackOverlay(QWidget):
                def __init__(self, user, script_dir):
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
                    self.status_label = QLabel(f"Face Unlock: Iniciando para {user}...")
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

                def update_status(self, message, progress_val):
                    self.status_label.setText(message)
                    self.progress.setValue(progress_val)
                    if any(x in message.upper() for x in ["SUCESSO", "OK", "CONCEDIDO"]):
                        self.status_label.setStyleSheet(
                            self.status_label.styleSheet() + "color: #2ecc71;"
                        )
                    elif any(x in message.upper() for x in ["FALHA", "ERRO", "NEGADA"]):
                        self.status_label.setStyleSheet(
                            self.status_label.styleSheet() + "color: #e74c3c;"
                        )

            # Inicialização
            self.app = QApplication.instance() or QApplication(sys.argv)
            # SCRIPT_DIR vem do ambiente ou relativo
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.overlay = FeedbackOverlay(username, script_dir)
            self.overlay.show()
            self.available = True
        except Exception:
            # Silêncio total em caso de erro gráfico
            self.available = False

    def update(self, message, progress=0):
        if self.available:
            try:
                self.overlay.update_status(message, progress)
                self.app.processEvents()
            except Exception:
                self.available = False

    def close(self):
        if self.available:
            try:
                self.overlay.close()
            except Exception:
                pass
