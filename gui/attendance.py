from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer
from core.camera import CameraManager
from core.attendance import AttendanceManager


class AttendancePage(QWidget):
    def __init__(self, db, recognition_engine):
        super().__init__()
        self.db = db
        self.recognition = recognition_engine
        self.attendance_mgr = AttendanceManager(db)
        self.camera_manager = CameraManager(recognition_engine)
        self.camera_manager.frame_ready.connect(self.update_frame)
        self.camera_manager.error.connect(self.show_error)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Video display
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid gray; background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label, alignment=Qt.AlignCenter)

        # Error label (non-intrusive)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Controls
        controls = QHBoxLayout()
        self.course_combo = QComboBox()
        self.course_combo.addItems(["Math", "Physics", "Chemistry", "Computer Science"])
        self.start_btn = QPushButton("Start Camera")
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.clicked.connect(self.stop_camera)
        controls.addWidget(QLabel("Course:"))
        controls.addWidget(self.course_combo)
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        layout.addLayout(controls)

        # Timer to auto-hide error message after 5 seconds
        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(lambda: self.error_label.setVisible(False))

    def start_camera(self):
        self.camera_manager.start()

    def stop_camera(self):
        self.camera_manager.stop()

    def update_frame(self, qimage: QImage):
        pixmap = QPixmap.fromImage(qimage).scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pixmap)

    def show_error(self, msg):
        # Show error text for a few seconds instead of a blocking dialog
        self.error_label.setText(msg)
        self.error_label.setVisible(True)
        self.error_timer.start(5000)   # hide after 5 seconds

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()