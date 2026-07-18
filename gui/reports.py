from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDateEdit, QComboBox, QLabel
from core.report import ReportGenerator
from PySide6.QtCore import QDate

class ReportsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.generator = ReportGenerator(db)
        layout = QVBoxLayout(self)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.format_combo = QComboBox()
        self.format_combo.addItems(["excel", "csv", "pdf"])
        btn = QPushButton("Generate Report")
        btn.clicked.connect(self.generate)
        layout.addWidget(QLabel("Select Date:"))
        layout.addWidget(self.date_edit)
        layout.addWidget(QLabel("Format:"))
        layout.addWidget(self.format_combo)
        layout.addWidget(btn)

    def generate(self):
        date = self.date_edit.date().toPython()
        fmt = self.format_combo.currentText()
        path = self.generator.daily_report(date, fmt=fmt)
        # show message with path