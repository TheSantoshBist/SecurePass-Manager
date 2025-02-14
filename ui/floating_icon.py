from PySide6.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QApplication)
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QIcon, QCursor

class FloatingWidget(QWidget):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setFixedSize(50, 50)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.icon_button = QPushButton()
        self.icon_button.setFixedSize(50, 50)
        self.icon_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 52, 54, 0.8);
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: rgba(9, 132, 227, 0.9);
            }
        """)
        self.icon_button.setIcon(QIcon("icon/logo.ico"))
        self.icon_button.setIconSize(QSize(30, 30))
        self.icon_button.clicked.connect(self.on_clicked)

        layout.addWidget(self.icon_button)
        self.move_to_edge()

        self.old_pos = None
        self.click_pos = None
        self.offset = None
        self.is_dragging = False

    def on_clicked(self):
        self.clicked.emit()

    def move_to_edge(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = screen_geometry.left()
        y = screen_geometry.center().y() - self.height() / 2
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.offset = event.globalPosition().toPoint() - self.pos()
            self.is_dragging = True
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        elif event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            if self.parent():
                self.parent().showNormal()
                self.parent().activateWindow()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.RightButton and self.is_dragging and self.offset:
            new_pos = event.globalPosition().toPoint() - self.offset

            # Keep widget within screen bounds
            screen = QApplication.primaryScreen().geometry()
            new_pos.setX(max(0, min(new_pos.x(), screen.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen.height() - self.height())))

            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.is_dragging = False
            self.offset = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def enterEvent(self, event):
        if not self.is_dragging:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def leaveEvent(self, event):
        if not self.is_dragging:
            self.setCursor(Qt.CursorShape.ArrowCursor)