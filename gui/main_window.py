from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QDialog, QLineEdit, QCheckBox, QDialogButtonBox,
    QMessageBox, QLabel
)
from PySide6.QtCore import Qt
import qdarkstyle

from gui.dashboard import DashboardPage
from gui.students import StudentsPage
from gui.attendance import AttendancePage
from gui.reports import ReportsPage
from gui.settings import SettingsPage
from database.database import SessionLocal, init_db
from core.recognition import RecognitionEngine
from database.models import User
import hashlib
import base64


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisionAttend AI - Login")
        self.setFixedSize(350, 250)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Password")
        self.remember_check = QCheckBox("Remember me")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(QLabel("Administrator Login"))
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.remember_check)
        layout.addWidget(buttons)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = SessionLocal()
        self.recognition_engine = RecognitionEngine(self.db)
        self.current_user = None

        self.setWindowTitle("VisionAttend AI")
        self.resize(1280, 800)
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        self.init_ui()

        # Login loop – keep asking until success or user cancels
        while True:
            if self.show_login():
                break   # login successful
            else:
                # User clicked Cancel on the login dialog
                self.close()
                return

        self.show()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #1e1e2d; border-radius: 0px;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)

        self.btn_dashboard = QPushButton("📊 Dashboard")
        self.btn_students = QPushButton("🎓 Students")
        self.btn_attendance = QPushButton("📸 Attendance")
        self.btn_reports = QPushButton("📄 Reports")
        self.btn_settings = QPushButton("⚙️ Settings")

        for btn in [self.btn_dashboard, self.btn_students,
                    self.btn_attendance, self.btn_reports, self.btn_settings]:
            btn.setCheckable(True)
            btn.setStyleSheet("text-align:left; padding:10px; border:none; color:white;")
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Pages
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(self.db)
        self.students_page = StudentsPage(self.db)
        self.attendance_page = AttendancePage(self.db, self.recognition_engine)
        self.reports_page = ReportsPage(self.db)
        self.settings_page = SettingsPage(self.db)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.students_page)
        self.stack.addWidget(self.attendance_page)
        self.stack.addWidget(self.reports_page)
        self.stack.addWidget(self.settings_page)

        main_layout.addWidget(self.stack)

        # Connect sidebar buttons
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_students.clicked.connect(lambda: self.switch_page(1))
        self.btn_attendance.clicked.connect(lambda: self.switch_page(2))
        self.btn_reports.clicked.connect(lambda: self.switch_page(3))
        self.btn_settings.clicked.connect(lambda: self.switch_page(4))

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate([self.btn_dashboard, self.btn_students,
                                 self.btn_attendance, self.btn_reports,
                                 self.btn_settings]):
            btn.setChecked(i == index)

    def show_login(self):
        login = LoginDialog()
        if login.exec() == QDialog.Accepted:
            username = login.username_edit.text().strip()
            password = login.password_edit.text().strip()
            if self.authenticate(username, password):
                self.current_user = username
                return True
            else:
                QMessageBox.critical(self, "Error", "Invalid credentials")
                return False   # will prompt again in the loop
        else:
            return None   # user cancelled

    def authenticate(self, username, password):
        user = self.db.query(User).filter_by(username=username).first()
        if not user:
            return False
        salt = base64.b64decode(user.salt)
        hash_ = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return hash_ == base64.b64decode(user.password_hash)

    def closeEvent(self, event):
        self.attendance_page.stop_camera()
        self.db.close()
        event.accept()