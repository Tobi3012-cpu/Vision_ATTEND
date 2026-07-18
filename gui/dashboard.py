from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QDate
from gui.widgets import StatCard
from database.models import Student, Attendance

class DashboardPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(title)

        cards_layout = QHBoxLayout()
        self.total_card = StatCard("Total Students", 0, "#3498db")
        self.present_card = StatCard("Present Today", 0, "#2ecc71")
        self.absent_card = StatCard("Absent Today", 0, "#e74c3c")
        cards_layout.addWidget(self.total_card)
        cards_layout.addWidget(self.present_card)
        cards_layout.addWidget(self.absent_card)
        layout.addLayout(cards_layout)

        # Placeholder for charts (you can add matplotlib later)
        chart_label = QLabel("📈 Attendance charts can be embedded here")
        chart_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_label)
        layout.addStretch()

    def refresh(self):
        total = self.db.query(Student).count()
        today = QDate.currentDate().toPython()
        present = self.db.query(Attendance).filter(
            Attendance.date == today
        ).distinct(Attendance.student_id).count()

        self.total_card.set_value(total)
        self.present_card.set_value(present)
        self.absent_card.set_value(total - present)