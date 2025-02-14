import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.login_window import LoginWindow
from PySide6.QtGui import QIcon
from utils.file_init import init_program_files  # Add this import

def main():
    # Initialize program files before starting the app
    init_program_files()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Consistent style across platforms

    # Set application-wide attributes
    app.setApplicationName("SecurePass Manager by Santosh Bist")
    app.setOrganizationName("SecurePass")
    app.setOrganizationDomain("securepass.local")

    # Set the application icon
    app.setWindowIcon(QIcon("icon/logo.ico"))  # Set the application icon

    # Create and show the login window
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()