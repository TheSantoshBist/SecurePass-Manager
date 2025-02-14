from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QDialog, QStatusBar, QComboBox,
                             QHeaderView, QMenu, QApplication, QToolButton, QMessageBox, QListWidget, QFileDialog)
from PySide6.QtCore import Qt, QSize, QProcess, QUrl, QEvent, QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QFont, QAction, QKeySequence, QDesktopServices, QPixmap, QPixmapCache
from database.db_manager import DatabaseManager
import sys
from utils.password_generator import PasswordGenerator
from utils.auth import Auth  # Fix: Changed from relative to absolute import
from .add_password_dialog import AddPasswordDialog
from .manage_categories_dialog import ManageCategoriesDialog
from import_export import ImportExportManager  # Import the new module
from .floating_icon import FloatingWidget  # Import the FloatingWidget

class LoadPasswordsThread(QThread):
    passwordsLoaded = Signal(list)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

    def run(self):
        passwords = self.db_manager.get_all_passwords()
        self.passwordsLoaded.emit(passwords)

class MainWindow(QMainWindow):
    def __init__(self, master_password):
        super().__init__()
        self.master_password = master_password
        # Initialize database manager early
        self.db = DatabaseManager(master_password)

        # Use QTimer to defer UI setup
        QTimer.singleShot(0, self.setup_ui)

        # Set window properties immediately
        self.setWindowTitle("SecurePass Manager by Santosh Bist")
        self.setMinimumSize(800, 600)

        self.password_gen = PasswordGenerator()
        self.passwords = []  # Store password data
        self.import_export_manager = ImportExportManager(master_password)  # Initialize ImportExportManager

        # Predefine button styles
        self.edit_button_style = """
            QPushButton {
                background-color: #00b894;
                border-radius: 4px;
                padding: 4px;
                min-height: 15px;
            }
            QPushButton:hover {
                background-color: #00a381;
            }
        """
        self.delete_button_style = """
            QPushButton {
                background-color: #d63031;
                border-radius: 4px;
                padding: 4px;
                min-height: 15px;
            }
            QPushButton:hover {
                background-color: #c02627;
            }
        """

        # Create floating widget
        self.floating_widget = FloatingWidget(self)
        self.floating_widget.clicked.connect(self.restore_from_floating)
        self.floating_widget.hide()

    def setup_ui(self):
        self.setWindowTitle("SecurePass Manager")
        self.setMinimumSize(1000, 700)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Apply dark theme
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #1e272e;
                color: #ffffff;
            }
        """)

        # Top toolbar
        toolbar = QHBoxLayout()

        # Search section
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background-color: #2d3436;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 5, 10, 5)

        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search passwords...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                padding: 5px;
                font-size: 14px;
                min-width: 250px;
                color: #ffffff;
            }
            QLineEdit::placeholder {
                color: #b2bec3;
            }
        """)
        self.search_input.textChanged.connect(self.handle_search)
        search_layout.addWidget(self.search_input)

        toolbar.addWidget(search_container)

        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories"])
        self.load_categories()
        self.category_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #485460;
                border-radius: 6px;
                min-width: 150px;
                background-color: #2d3436;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d3436;
                color: white;
                selection-background-color: #0984e3;
            }
        """)
        self.category_filter.currentTextChanged.connect(self.filter_passwords)
        toolbar.addWidget(self.category_filter)

        toolbar.addStretch()

        # Add import and export buttons
        self.export_button = QPushButton("📤")  # Export icon
        self.export_button.setToolTip("Export Passwords")
        self.export_button.clicked.connect(self.export_passwords)
        self.export_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        toolbar.addWidget(self.export_button)

        self.import_button = QPushButton("📥")  # Import icon
        self.import_button.setToolTip("Import Passwords")
        self.import_button.clicked.connect(self.import_passwords)
        self.import_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        toolbar.addWidget(self.import_button)

        # Add manage categories button
        manage_cat_btn = QPushButton("Manage Categories")
        manage_cat_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #00b894;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00a381;
            }
        """)
        manage_cat_btn.clicked.connect(self.show_categories_dialog)
        toolbar.addWidget(manage_cat_btn)

        # Add spacing between buttons
        toolbar.addSpacing(10)

        # Add reset account button to toolbar
        reset_btn = QPushButton("🔄")  # Reset icon
        reset_btn.setToolTip("Reset Account")
        reset_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #d63031;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c02627;
            }
        """)
        reset_btn.clicked.connect(self.reset_account)
        toolbar.addWidget(reset_btn)

        # Add spacing between reset and add buttons
        toolbar.addSpacing(10)

        # Add button with icon
        add_btn = QPushButton("➕")  # Plus icon
        add_btn.setToolTip("Add New Password")
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #0984e3;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0773c5;
            }
        """)
        add_btn.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(add_btn)

        layout.addLayout(toolbar)

        # Password table setup with disabled editing
        self.password_table = QTableWidget()
        self.password_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Disable editing
        self.password_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)  # Disable selection
        self.password_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.password_table.customContextMenuRequested.connect(self.show_context_menu)
        self.password_table.setColumnCount(9)  # Added one more column for actions
        self.password_table.setHorizontalHeaderLabels(
            ["Website", "Copy", "Username", "Copy", "Password", "Copy", "Category", "Last Modified", "Actions"])

        # Add keyboard shortcuts
        copy_url_shortcut = QAction("Copy URL", self)
        copy_url_shortcut.setShortcut(QKeySequence.StandardKey.Copy)
        copy_url_shortcut.triggered.connect(lambda: self.copy_cell_content(0))
        self.addAction(copy_url_shortcut)

        # Update table style to remove selection highlighting
        self.password_table.setStyleSheet("""
            QTableWidget {
                background-color: #2d3436;
                color: white;
                gridline-color: #485460;
                border: 1px solid #485460;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #1e272e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                color: white;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: transparent;
                color: white;
            }
            QTableWidget::item:focus {
                background-color: transparent;
                color: white;
                border: none;
            }
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 11px;
                min-height: 15px;
            }
            QPushButton:hover {
                background-color: #0773c5;
            }
        """)

        # Set row height
        self.password_table.verticalHeader().setDefaultSectionSize(40)

        # Adjust column widths
        header = self.password_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Website
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Copy button
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Username
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Copy button
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Password
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Copy button
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Category
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Last Modified
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)    # Actions column

        # Set fixed width for copy button columns
        self.password_table.setColumnWidth(1, 60)
        self.password_table.setColumnWidth(3, 60)
        self.password_table.setColumnWidth(5, 60)
        self.password_table.setColumnWidth(8, 100)  # Width for actions column

        layout.addWidget(self.password_table)

        # Add status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2d3436;
                color: #b2bec3;
            }
        """)
        self.setStatusBar(self.status_bar)

        # Copyright label
        self.copyright_label = QLabel(
            '<a href="https://sbist.com.np" style="color:#b2bec3;">Open Source By Santosh Bist | Donate</a>'
        )
        self.copyright_label.setOpenExternalLinks(True)
        self.copyright_label.setStyleSheet("QStatusBar::item {border: none;}")
        self.status_bar.addPermanentWidget(self.copyright_label)

        # Load passwords in a separate thread
        self.load_passwords()

    def filter_passwords(self, category: str):
        # Clear the table
        self.password_table.setRowCount(0)

        # Fetch all passwords first
        all_passwords = self.db.get_all_passwords()

        # Filter passwords based on category from fetched data
        filtered_passwords = all_passwords
        if category != "All Categories":
            filtered_passwords = [p for p in all_passwords if p['category'] == category]

        # Load the filtered passwords into the table
        self.load_passwords_into_table(filtered_passwords)

        # Update status bar
        self.status_bar.showMessage(f"Showing {len(filtered_passwords)} passwords for category: {category if category != 'All Categories' else 'All'}")


    def load_passwords(self):
        self.load_passwords_thread = LoadPasswordsThread(self.db)
        self.load_passwords_thread.passwordsLoaded.connect(self.load_passwords_into_table)
        self.load_passwords_thread.start()

    def load_passwords_into_table(self, passwords):
        self.passwords = passwords
        self.password_table.setRowCount(0)

        if passwords:
            for password in passwords:
                row = self.password_table.rowCount()
                self.password_table.insertRow(row)

                # Website
                website_item = QTableWidgetItem(password['website'])
                website_item.setData(Qt.ItemDataRole.UserRole, password['id'])
                self.password_table.setItem(row, 0, website_item)

                # Add copy buttons
                self.add_copy_button(row, 1, password['website'], "URL")
                self.password_table.setItem(row, 2, QTableWidgetItem(password['username']))
                self.add_copy_button(row, 3, password['username'], "Username")
                self.password_table.setItem(row, 4, QTableWidgetItem('••••••••'))
                self.add_copy_button(row, 5, password['password'], "Password")

                # Category and timestamp
                self.password_table.setItem(row, 6, QTableWidgetItem(password['category']))
                self.password_table.setItem(row, 7, QTableWidgetItem(password['updated_at']))

                # Add actions buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(4)

                edit_btn = QPushButton("✏️")
                edit_btn.setToolTip("Edit")
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_password(r))
                edit_btn.setStyleSheet(self.edit_button_style)

                delete_btn = QPushButton("🗑️")
                delete_btn.setToolTip("Delete")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_password(r))
                delete_btn.setStyleSheet(self.delete_button_style)

                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()

                self.password_table.setCellWidget(row, 8, actions_widget)

        self.status_bar.showMessage(f"Loaded {len(passwords)} passwords")

    def handle_search(self, query: str):
        if not query:
            # If search is empty, show all passwords and apply category filter
            self.load_passwords()
            return

        # Search in database
        results = self.db.search_passwords(query)

        # Clear current table
        self.password_table.setRowCount(0)

        # Show search results
        if results:
            for password in results:
                row = self.password_table.rowCount()
                self.password_table.insertRow(row)

                # Website with ID
                website_item = QTableWidgetItem(password['website'])
                website_item.setData(Qt.ItemDataRole.UserRole, password['id'])
                self.password_table.setItem(row, 0, website_item)

                # Add copy buttons and other fields
                self.add_copy_button(row, 1, password['website'], "URL")
                self.password_table.setItem(row, 2, QTableWidgetItem(password['username']))
                self.add_copy_button(row, 3, password['username'], "Username")
                self.password_table.setItem(row, 4, QTableWidgetItem('••••••••'))
                self.add_copy_button(row, 5, password['password'], "Password")
                self.password_table.setItem(row, 6, QTableWidgetItem(password['category']))
                self.password_table.setItem(row, 7, QTableWidgetItem(password['updated_at']))

                # Add action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                actions_layout.setSpacing(4)

                # Edit button
                edit_btn = QPushButton("✏️")
                edit_btn.setToolTip("Edit")
                edit_btn.clicked.connect(lambda checked, r=row: self.edit_password(r))
                edit_btn.setStyleSheet(self.edit_button_style)

                # Delete button
                delete_btn = QPushButton("🗑️")
                delete_btn.setToolTip("Delete")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_password(r))
                delete_btn.setStyleSheet(self.delete_button_style)

                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()

                self.password_table.setCellWidget(row, 8, actions_widget)

        # Update status bar with search results count
        self.status_bar.showMessage(f"Found {self.password_table.rowCount()} passwords matching '{query}'")

    def show_add_dialog(self):
        # Refresh categories just before showing the dialog
        categories = self.db.get_all_categories()
        dialog = AddPasswordDialog(parent=self, categories=categories) # Pass self (MainWindow) as parent and categories
        if dialog.exec() == QDialog.DialogCode.Accepted:
            values = dialog.get_values()
            self.db.add_password(
                website=values['website'],
                username=values['username'],
                password=values['password'],
                category=values['category'],
                tags=values['tags']
            )
            self.load_passwords()  # Refresh the table

    def show_context_menu(self, position):
        menu = QMenu()
        copy_action = QAction("Copy Password", self)
        copy_action.triggered.connect(self.copy_password)
        menu.addAction(copy_action)

        global_pos = self.password_table.mapToGlobal(position)
        menu.exec(global_pos)

    def copy_password(self):
        current_row = self.password_table.currentRow()
        if current_row >= 0:
            password_id = self.password_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            # Get the actual password from database
            password_data = self.db.get_password(password_id)
            if password_data:
                # Copy to clipboard
                QApplication.clipboard().setText(password_data['password'])
                self.status_bar.showMessage("Password copied to clipboard", 2000)

    def add_copy_button(self, row: int, column: int, content: str, label: str):
        btn = QPushButton("Copy")
        btn.clicked.connect(lambda: self.copy_to_clipboard(content, label))
        self.password_table.setCellWidget(row, column, btn)

    def copy_to_clipboard(self, content: str, label: str):
        QApplication.clipboard().setText(content)
        self.status_bar.showMessage(f"{label} copied to clipboard", 2000)

    def copy_cell_content(self, column: int):
        current_row = self.password_table.currentRow()
        if current_row >= 0:
            if column == 0:  # Website
                content = self.password_table.item(current_row, 0).text()
                self.copy_to_clipboard(content, "URL")
            elif column == 2:  # Username
                content = self.password_table.item(current_row, 2).text()
                self.copy_to_clipboard(content, "Username")
            elif column == 4:  # Password
                password_id = self.password_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
                password_data = self.db.get_password(password_id)
                if password_data:
                    self.copy_to_clipboard(password_data['password'], "Password")

    def edit_password(self, row: int):
        password_id = self.password_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        password_data = self.db.get_password(password_id)
        if password_data:
            dialog = AddPasswordDialog(parent=self, categories=self.db.get_all_categories())  # pass parent and categories
            dialog.website_input.setText(password_data['website'])
            dialog.username_input.setText(password_data['username'])
            dialog.password_input.setText(password_data['password'])

            # Set the category by finding the index
            category_index = dialog.category_input.findText(password_data['category'])
            if category_index != -1:
                dialog.category_input.setCurrentIndex(category_index)
            else:
                # If category not found, add it and set as current
                dialog.category_input.addItem(password_data['category'])
                dialog.category_input.setCurrentText(password_data['category'])

            dialog.tags_input.setText(password_data['tags'] or '')

            if dialog.exec() == QDialog.DialogCode.Accepted:
                values = dialog.get_values()
                self.db.update_password(
                    password_id,
                    website=values['website'],
                    username=values['username'],
                    password=values['password'],
                    category=values['category'],
                    tags=values['tags']
                )
                self.load_passwords()

    def delete_password(self, row: int):
        password_id = self.password_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        website = self.password_table.item(row, 0).text()

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the password for {website}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_password(password_id)
            self.load_passwords()
            self.status_bar.showMessage(f"Deleted password for {website}")

    def reset_account(self):
        reply = QMessageBox.warning(
            self,
            "Reset Account",
            "Are you sure you want to reset your account?\n\n"
            "This will:\n"
            "• Delete all saved passwords\n"
            "• Reset master password\n"
            "• Require new setup\n\n"
            "This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            confirm = QMessageBox.warning(
                self,
                "Confirm Reset",
                "Last warning: All data will be permanently deleted.\n"
                "Are you absolutely sure?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                self.db.reset_database()
                self.auth = Auth()
                self.auth.reset_master_password()

                QMessageBox.information(
                    self,
                    "Reset Complete",
                    "Your account has been reset.\n"
                    "The application will now restart for a fresh setup."
                )

                # Restart application
                QApplication.quit()
                QProcess.startDetached(sys.executable, sys.argv)

    def show_categories_dialog(self):
        # Get current categories from combobox
        current_categories = [self.category_filter.itemText(i)
                            for i in range(self.category_filter.count())
                            if self.category_filter.itemText(i) != "All Categories"]

        dialog = ManageCategoriesDialog(self, current_categories)
        dialog.categoriesChanged.connect(self.update_categories)
        dialog.exec()

    def update_categories(self, new_categories):
        # Update category filter combobox
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(new_categories)

        # Refresh the table to show updated categories and filter
        current_category_filter = self.category_filter.currentText()
        self.filter_passwords(current_category_filter) # Re-apply the current filter, or "All Categories" if none selected

    def load_categories(self):
        categories = self.db.get_all_categories()
        self.category_filter.addItems(categories)

    def export_passwords(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getSaveFileName(self, "Export Passwords", "", "Encrypted Files (*.enc)")
        if filename:
            # Fetch all passwords from the database
            passwords = self.db.get_all_passwords()

            # Export the passwords using the ImportExportManager
            if self.import_export_manager.export_passwords(passwords, filename):
                self.status_bar.showMessage(f"Passwords exported to {filename}", 5000)
            else:
                QMessageBox.critical(self, "Error", "Failed to export passwords.")

    def import_passwords(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, "Import Passwords", "", "Encrypted Files (*.enc)")
        if filename:
            # Import the passwords using the ImportExportManager
            passwords = self.import_export_manager.import_passwords(filename)

            if passwords:
                # Add the imported passwords to the database
                for password in passwords:
                    self.db.add_password(
                        website=password['website'],
                        username=password['username'],
                        password=password['password'],
                        category=password['category'],
                        tags=password['tags']
                    )
                self.load_passwords()  # Refresh the table
                self.status_bar.showMessage(f"Passwords imported from {filename}", 5000)
            else:
                QMessageBox.critical(self, "Error", "Failed to import passwords.")

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                self.floating_widget.show()
            else:
                self.floating_widget.hide()
        super().changeEvent(event)

    def restore_from_floating(self):
        self.setWindowState(Qt.WindowState.WindowActive)  # Ensure window is active
        self.showNormal()  # Restore window to normal size
        self.activateWindow()  # Bring window to the front