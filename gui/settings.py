"""
Settings page: camera selection, recognition threshold, theme, backup/restore.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QSlider, QComboBox, QFileDialog, QMessageBox,
    QApplication
)
from PySide6.QtCore import Qt
import qdarkstyle
from database.models import Setting
from sqlalchemy.orm import Session
import shutil
import os


class SettingsPage(QWidget):
    def __init__(self, db_session: Session):
        super().__init__()
        self.db = db_session
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # ---- Camera group ----
        camera_group = QGroupBox("Camera")
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("Camera Index:"))
        self.camera_combo = QComboBox()
        for i in range(5):          # 0 to 4 common USB cameras
            self.camera_combo.addItem(str(i))
        camera_layout.addWidget(self.camera_combo)
        camera_group.setLayout(camera_layout)
        main_layout.addWidget(camera_group)

        # ---- Recognition Threshold ----
        threshold_group = QGroupBox("Recognition Threshold")
        th_layout = QHBoxLayout()
        th_layout.addWidget(QLabel("Strict"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(1, 100)
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        th_layout.addWidget(self.threshold_slider)
        th_layout.addWidget(QLabel("Relaxed"))
        self.threshold_value_label = QLabel()
        th_layout.addWidget(self.threshold_value_label)
        threshold_group.setLayout(th_layout)
        main_layout.addWidget(threshold_group)

        # ---- Theme group ----
        theme_group = QGroupBox("Appearance")
        theme_layout = QHBoxLayout()
        self.dark_btn = QPushButton("Dark Mode")
        self.dark_btn.setCheckable(True)
        self.light_btn = QPushButton("Light Mode")
        self.light_btn.setCheckable(True)
        self.dark_btn.clicked.connect(lambda: self.set_theme("dark"))
        self.light_btn.clicked.connect(lambda: self.set_theme("light"))
        theme_layout.addWidget(self.dark_btn)
        theme_layout.addWidget(self.light_btn)
        theme_group.setLayout(theme_layout)
        main_layout.addWidget(theme_group)

        # ---- Backup / Restore ----
        backup_group = QGroupBox("Database")
        backup_layout = QHBoxLayout()
        backup_btn = QPushButton("Backup Database")
        restore_btn = QPushButton("Restore Database")
        backup_btn.clicked.connect(self.backup_db)
        restore_btn.clicked.connect(self.restore_db)
        backup_layout.addWidget(backup_btn)
        backup_layout.addWidget(restore_btn)
        backup_group.setLayout(backup_layout)
        main_layout.addWidget(backup_group)

        # ---- Save button ----
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        main_layout.addWidget(save_btn)
        main_layout.addStretch()

    def load_settings(self):
        # Camera index
        cam = self.db.query(Setting).filter_by(key="camera_index").first()
        if cam:
            self.camera_combo.setCurrentText(cam.value)

        # Threshold
        th = self.db.query(Setting).filter_by(key="recognition_threshold").first()
        if th:
            self.threshold_slider.setValue(int(float(th.value) * 100))
        else:
            self.threshold_slider.setValue(50)
        self.update_threshold_label()
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)

        # Theme
        theme = self.db.query(Setting).filter_by(key="theme").first()
        current_theme = theme.value if theme else "dark"
        self.set_theme_buttons(current_theme)

    def update_threshold_label(self):
        value = self.threshold_slider.value() / 100.0
        self.threshold_value_label.setText(f"{value:.2f}")

    def set_theme(self, theme_name):
        """Apply dark/light theme to entire application."""
        app = QApplication.instance()
        if app:
            if theme_name == "dark":
                app.setStyleSheet(qdarkstyle.load_stylesheet())
            else:
                app.setStyleSheet("")      # revert to default light theme
        self.set_theme_buttons(theme_name)

    def set_theme_buttons(self, theme_name):
        self.dark_btn.setChecked(theme_name == "dark")
        self.light_btn.setChecked(theme_name == "light")

    def save_settings(self):
        camera_idx = self.camera_combo.currentText()
        threshold = self.threshold_slider.value() / 100.0
        theme = "dark" if self.dark_btn.isChecked() else "light"

        for key, value in [
            ("camera_index", camera_idx),
            ("recognition_threshold", str(threshold)),
            ("theme", theme)
        ]:
            setting = self.db.query(Setting).filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                self.db.add(Setting(key=key, value=value))
        self.db.commit()
        QMessageBox.information(self, "Settings",
                                "Settings saved. Some changes may need a restart.")

    def backup_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", "", "Database Files (*.db)"
        )
        if path:
            try:
                shutil.copy2("database/attendance.db", path)
                QMessageBox.information(self, "Backup",
                                        f"Database backed up to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def restore_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Restore Database", "", "Database Files (*.db)"
        )
        if path:
            reply = QMessageBox.warning(
                self, "Confirm Restore",
                "This will replace the current database. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    shutil.copy2(path, "database/attendance.db")
                    QMessageBox.information(self, "Restore",
                                            "Database restored. Please restart the application.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))