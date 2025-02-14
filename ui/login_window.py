from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from utils.auth import Auth
from ui.main_window import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.auth = Auth()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("SecurePass Manager - Login")
        self.setFixedSize(400, 350)  # Increased height
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set window transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Style the central widget with proper background and borders
        central_widget.setStyleSheet("""
            QWidget#centralWidget {
                background-color: white;
                border: 2px solid #dfe6e9;
                border-radius: 15px;
            }
        """)
        central_widget.setObjectName("centralWidget")

        # Remove the old main window style and replace with transparent background
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)  # Add spacing between widgets
        layout.setContentsMargins(20, 20, 20, 20)  # Add margins

        # Add close button at top-right
        top_layout = QHBoxLayout()
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5f57;
                border-radius: 15px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff3b36;
            }
        """)
        top_layout.addStretch()
        top_layout.addWidget(close_button)
        layout.addLayout(top_layout)

        # Create title section with icon
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)  # Control space between icon and text
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the entire layout

        # Add lock icon
        icon_label = QLabel()
        icon_pixmap = QPixmap("icon/lock.png")
        icon_label.setPixmap(icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(icon_label)

        # Add title
        title = QLabel("SecurePass Manager")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title.setStyleSheet("color: #2d3436;")
        title_layout.addWidget(title)

        layout.addLayout(title_layout)

        # Create password input field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter master password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Create confirm password field (only shown during first setup)
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm master password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Create status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Style input fields with better colors and borders
        input_style = """
            QLineEdit {
                padding: 12px;
                border: 2px solid #dfe6e9;
                border-radius: 8px;
                background-color: #f5f6fa;
                font-size: 14px;
                color: #2d3436;
            }
            QLineEdit:focus {
                border: 2px solid #0984e3;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #b2bec3;
            }
        """

        self.password_input.setStyleSheet(input_style)
        layout.addWidget(self.password_input)

        self.confirm_password.setStyleSheet(input_style)
        layout.addWidget(self.confirm_password)

        # Style status label
        self.status_label.setStyleSheet("color: #636e72; font-size: 13px;")
        layout.addWidget(self.status_label)

        # Style login button
        self.login_button = QPushButton("Login" if self.auth.has_master_password() else "Set Password")
        self.login_button.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background-color: #0984e3;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0773c5;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        layout.addStretch()  # Add space at bottom

        # Update visibility based on whether master password exists
        self.update_status()

        # Make window draggable
        self.oldPos = None
        central_widget.mousePressEvent = self.mousePressEvent
        central_widget.mouseMoveEvent = self.mouseMoveEvent

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def update_status(self):
        if self.auth.has_master_password():
            self.status_label.setText("Enter your master password to unlock")
            self.confirm_password.hide()  # Hide confirm field during login
            self.login_button.setText("Login")
        else:
            self.status_label.setText("First time setup - Create your master password")
            self.confirm_password.show()  # Show confirm field during setup
            self.login_button.setText("Set Password")

    def handle_login(self):
        password = self.password_input.text()

        if not self.auth.has_master_password():
            # First time setup
            confirm_pass = self.confirm_password.text()
            if password != confirm_pass:
                QMessageBox.warning(self, "Error", "Passwords do not match!")
                return
            if len(password) < 8:
                QMessageBox.warning(self, "Error", "Password must be at least 8 characters!")
                return

            self.auth.set_master_password(password)
            QMessageBox.information(self, "Success", "Master password set successfully!")
            self.update_status()

        else:
            # Regular login
            if self.auth.verify_password(password):
                # Show loading indicator
                self.login_button.setEnabled(False)
                self.login_button.setText("Loading...")

                # Use QTimer to create the main window asynchronously
                QTimer.singleShot(100, lambda: self._create_main_window(password))
            else:
                QMessageBox.warning(self, "Error", "Incorrect password!")

    def _create_main_window(self, password):
        self.main_window = MainWindow(password)
        self.main_window.show()
        self.close()