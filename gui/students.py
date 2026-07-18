"""
Student management page – add, edit, delete, import/export, capture faces.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QFileDialog, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox
)
from database.models import Student
from core.registration import RegistrationManager
import pandas as pd


class StudentsPage(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by ID or name...")
        self.search_bar.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_bar)

        # Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Student ID", "First Name", "Last Name",
            "Department", "Course", "Email"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student)
        edit_btn = QPushButton("Edit Student")
        edit_btn.clicked.connect(self.edit_student)
        delete_btn = QPushButton("Delete Student")
        delete_btn.clicked.connect(self.delete_student)
        capture_btn = QPushButton("Capture Faces")
        capture_btn.clicked.connect(self.capture_faces)
        import_btn = QPushButton("Import Excel")
        import_btn.clicked.connect(self.import_excel)
        export_btn = QPushButton("Export Excel")
        export_btn.clicked.connect(self.export_excel)

        for btn in [add_btn, edit_btn, delete_btn, capture_btn,
                    import_btn, export_btn]:
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.load_table()

    def load_table(self, filter_text=""):
        """Refresh table from database, optionally filtered."""
        students = self.db.query(Student).all()
        if filter_text:
            text = filter_text.lower()
            students = [
                s for s in students
                if text in s.student_id.lower()
                or text in s.first_name.lower()
                or text in s.last_name.lower()
            ]
        self.table.setRowCount(len(students))
        for row, s in enumerate(students):
            self.table.setItem(row, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(row, 1, QTableWidgetItem(s.student_id))
            self.table.setItem(row, 2, QTableWidgetItem(s.first_name))
            self.table.setItem(row, 3, QTableWidgetItem(s.last_name))
            self.table.setItem(row, 4, QTableWidgetItem(s.department or ""))
            self.table.setItem(row, 5, QTableWidgetItem(s.course or ""))
            self.table.setItem(row, 6, QTableWidgetItem(s.email or ""))

    def filter_table(self, text):
        self.load_table(text)

    def add_student(self):
        dialog = StudentDialog(self.db)
        if dialog.exec():
            self.load_table()

    def edit_student(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Please select a student to edit.")
            return
        student_id = int(self.table.item(row, 0).text())
        student = self.db.query(Student).filter_by(id=student_id).first()
        if student:
            dialog = StudentDialog(self.db, student)
            if dialog.exec():
                self.load_table()

    def delete_student(self):
        row = self.table.currentRow()
        if row < 0:
            return
        student_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Delete this student and all related data?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.query(Student).filter_by(id=student_id).delete()
            self.db.commit()
            self.load_table()

    def capture_faces(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Select a student first.")
            return
        student_id_str = self.table.item(row, 1).text()
        try:
            reg_manager = RegistrationManager(self.db)
            num = reg_manager.capture_faces(student_id_str, num_images=30)
            QMessageBox.information(
                self, "Capture Complete",
                f"Captured {num} images and stored embeddings."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Students", "",
            "Excel Files (*.xlsx *.xls)"
        )
        if not path:
            return
        try:
            df = pd.read_excel(path)
            for _, row in df.iterrows():
                s = Student(
                    student_id=str(row.get("student_id", "")),
                    first_name=str(row.get("first_name", "")),
                    last_name=str(row.get("last_name", "")),
                    department=str(row.get("department", "")),
                    course=str(row.get("course", "")),
                    email=str(row.get("email", "")),
                    phone=str(row.get("phone", "")),
                    gender=str(row.get("gender", ""))
                )
                self.db.add(s)
            self.db.commit()
            self.load_table()
            QMessageBox.information(self, "Import", "Students imported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Students", "",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return
        try:
            students = self.db.query(Student).all()
            data = []
            for s in students:
                data.append({
                    "student_id": s.student_id,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "department": s.department or "",
                    "course": s.course or "",
                    "email": s.email or "",
                    "phone": s.phone or "",
                    "gender": s.gender or ""
                })
            df = pd.DataFrame(data)
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Export", f"Exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))


class StudentDialog(QDialog):
    """Dialog for adding/editing a student."""
    def __init__(self, db, student=None):
        super().__init__()
        self.db = db
        self.student = student
        self.setWindowTitle("Add Student" if student is None else "Edit Student")
        self.setFixedSize(400, 350)
        self.setup_ui()
        if student:
            self.populate_fields()

    def setup_ui(self):
        layout = QFormLayout(self)
        self.student_id_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.dept_edit = QLineEdit()
        self.course_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()

        layout.addRow("Student ID:", self.student_id_edit)
        layout.addRow("First Name:", self.first_name_edit)
        layout.addRow("Last Name:", self.last_name_edit)
        layout.addRow("Department:", self.dept_edit)
        layout.addRow("Course:", self.course_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Phone:", self.phone_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def populate_fields(self):
        self.student_id_edit.setText(self.student.student_id)
        self.first_name_edit.setText(self.student.first_name)
        self.last_name_edit.setText(self.student.last_name)
        self.dept_edit.setText(self.student.department or "")
        self.course_edit.setText(self.student.course or "")
        self.email_edit.setText(self.student.email or "")
        self.phone_edit.setText(self.student.phone or "")

    def accept(self):
        sid = self.student_id_edit.text().strip()
        if not sid:
            QMessageBox.warning(self, "Validation", "Student ID is required.")
            return
        if self.student is None:
            # Adding new
            if self.db.query(Student).filter_by(student_id=sid).first():
                QMessageBox.warning(self, "Duplicate", "Student ID already exists.")
                return
            student = Student(
                student_id=sid,
                first_name=self.first_name_edit.text().strip(),
                last_name=self.last_name_edit.text().strip(),
                department=self.dept_edit.text().strip(),
                course=self.course_edit.text().strip(),
                email=self.email_edit.text().strip(),
                phone=self.phone_edit.text().strip()
            )
            self.db.add(student)
        else:
            # Editing
            self.student.student_id = sid
            self.student.first_name = self.first_name_edit.text().strip()
            self.student.last_name = self.last_name_edit.text().strip()
            self.student.department = self.dept_edit.text().strip()
            self.student.course = self.course_edit.text().strip()
            self.student.email = self.email_edit.text().strip()
            self.student.phone = self.phone_edit.text().strip()
        self.db.commit()
        super().accept()