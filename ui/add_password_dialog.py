from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QLabel, QComboBox, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt
from utils.password_generator import PasswordGenerator

class AddPasswordDialog(QDialog):
    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.password_gen = PasswordGenerator()
        # Categories are now fetched dynamically when dialog is created
        self.categories = categories if categories is not None else [] # keep categories as an attribute for initial setup, but reload later.
        self.db = parent.db if parent else None # Access db from parent if available
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Add New Password")
        self.setFixedSize(400, 450)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Website
        layout.addWidget(QLabel("Website:"))
        self.website_input = QLineEdit()
        layout.addWidget(self.website_input)

        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Password
        layout.addWidget(QLabel("Password:"))
        pass_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.password_input)

        gen_pass_btn = QPushButton("Generate")
        gen_pass_btn.clicked.connect(self.generate_password)
        pass_layout.addWidget(gen_pass_btn)
        layout.addLayout(pass_layout)

        # Category
        layout.addWidget(QLabel("Category:"))
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        if self.db: # Fetch categories from db every time dialog is shown
            fresh_categories = self.db.get_all_categories()
            self.category_input.clear() # Clear old items
            self.category_input.addItems(fresh_categories) # Add fresh categories
        else:
             self.category_input.addItems(self.categories) # fallback if db is not accessible during initial setup.

        layout.addWidget(self.category_input)

        # Tags
        layout.addWidget(QLabel("Tags (comma separated):"))
        self.tags_input = QLineEdit()
        layout.addWidget(self.tags_input)

        # Set fixed height for input fields
        for widget in [self.website_input, self.username_input,
                      self.password_input, self.tags_input]:
            widget.setFixedHeight(38)

        self.category_input.setFixedHeight(38)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e272e;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 13px;
                margin-bottom: 2px;
            }
            QLineEdit, QComboBox {
                padding: 8px 12px;
                border: 2px solid #485460;
                border-radius: 6px;
                background-color: #2d3436;
                color: white;
                min-height: 20px;
                font-size: 13px;
                margin-bottom: 5px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #0984e3;
            }
            QLineEdit::placeholder {
                color: #b2bec3;
            }
            QComboBox {
                min-height: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d3436;
                color: white;
                selection-background-color: #0984e3;
                padding: 4px;
            }
            QPushButton {
                padding: 5px 16px;
                border-radius: 6px;
                color: white;
                background-color: #0984e3;
                min-height: 20px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0773c5;
            }
            QPushButton[text="Cancel"] {
                background-color: #636e72;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #535c60;
            }
            QPushButton[text="Generate"] {
                background-color: #00b894;
                min-height: 25px;
            }
            QPushButton[text="Generate"]:hover {
                background-color: #00a381;
            }
        """)

    def generate_password(self):
        password = self.password_gen.generate()
        self.password_input.setText(password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)

    def get_values(self):
        return {
            'website': self.website_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'category': self.category_input.currentText(),
            'tags': self.tags_input.text()
        }