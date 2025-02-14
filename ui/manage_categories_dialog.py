from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QPushButton, QLabel, QListWidget)
from PySide6.QtCore import Qt, Signal

class ManageCategoriesDialog(QDialog):
    # Signal to notify when categories are updated
    categoriesChanged = Signal(list)

    def __init__(self, parent=None, current_categories=None):
        super().__init__(parent)
        self.db = parent.db  # Access the database from the main window
        self.default_categories = []
        self.current_categories = current_categories or self.default_categories
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Manage Categories")
        self.setFixedSize(300, 400)
        layout = QVBoxLayout(self)

        # Style the dialog
        self.apply_styles()

        # Add category input and button
        input_layout = QHBoxLayout()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("New category name")
        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("background-color: #0984e3;")
        input_layout.addWidget(self.category_input)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        # Category list
        self.category_list = QListWidget()
        self.category_list.addItems(self.current_categories)
        layout.addWidget(self.category_list)

        # Action buttons
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: #d63031;")
        close_btn = QPushButton("Save & Close")
        close_btn.setStyleSheet("background-color: #00b894;")
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        # Connect actions
        add_btn.clicked.connect(self.add_category)
        delete_btn.clicked.connect(self.delete_category)
        close_btn.clicked.connect(self.save_and_close)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e272e;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #485460;
                border-radius: 6px;
                background-color: #2d3436;
                color: white;
                min-height: 20px;
            }
            QListWidget {
                background-color: #2d3436;
                color: white;
                border: 1px solid #485460;
                border-radius: 6px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #0984e3;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                min-height: 25px;
            }
        """)

    def add_category(self):
        category = self.category_input.text().strip()
        current_categories = {self.category_list.item(i).text() for i in range(self.category_list.count())}
        if category and category not in current_categories:
            self.category_list.addItem(category)
            self.category_input.clear()

    def delete_category(self):
        current_item = self.category_list.currentItem()
        default_categories_set = set(self.default_categories)
        if current_item and current_item.text() not in default_categories_set:
            self.category_list.takeItem(self.category_list.row(current_item))

    def save_and_close(self):
        new_categories = [self.category_list.item(i).text()
                     for i in range(self.category_list.count())]

        # Add new categories to the database
        for category in new_categories:
            if category not in self.current_categories:
                self.db.add_category(category)

        # Delete removed categories from the database
        for category in self.current_categories:
            if category not in new_categories:
                self.db.delete_category(category)

        self.categoriesChanged.emit(new_categories)
        self.accept()