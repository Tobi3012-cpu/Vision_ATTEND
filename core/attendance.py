from datetime import datetime, date, time
from database.models import Attendance, Student
from sqlalchemy import and_

class AttendanceManager:
    def __init__(self, db_session):
        self.db = db_session

    def mark_attendance(self, student_id: str, course: str, status="Present"):
        student = self.db.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return False
        today = date.today()
        existing = self.db.query(Attendance).filter(
            and_(Attendance.student_id == student.id,
                 Attendance.date == today,
                 Attendance.course == course)
        ).first()
        if existing:
            return False   # already marked

        att = Attendance(
            student_id=student.id,
            date=today,
            time=datetime.now().time(),
            course=course,
            status=status
        )
        self.db.add(att)
        self.db.commit()
        return True

    def get_today_attendance(self, course=None):
        today = date.today()
        query = self.db.query(Attendance).filter(Attendance.date == today)
        if course:
            query = query.filter(Attendance.course == course)
        return query.all()