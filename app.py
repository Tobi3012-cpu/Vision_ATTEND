import sys
from PySide6.QtWidgets import QApplication
from database.database import init_db
from gui.main_window import MainWindow

def main():
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()