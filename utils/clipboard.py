from PySide6.QtCore import QTimer
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

class ClipboardManager:
    def __init__(self, clear_delay: int = 5000):
        self.clipboard = QApplication.clipboard()
        self.clear_delay = clear_delay  # milliseconds
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self.clear_clipboard)

    def copy_to_clipboard(self, text: str):
        self.clipboard.setText(text)
        self.clear_timer.start(self.clear_delay)

    def clear_clipboard(self):
        self.clipboard.clear()
        self.clear_timer.stop()