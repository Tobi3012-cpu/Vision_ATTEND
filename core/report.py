import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Attendance, Student
from config import EXPORTS_DIR
import os

class ReportGenerator:
    def __init__(self, db_session: Session):
        self.db = db_session

    def daily_report(self, date, course=None, export_format='excel'):
        query = self.db.query(Attendance).filter(Attendance.date == date)
        if course:
            query = query.filter(Attendance.course == course)
        records = query.all()
        data = [{
            'Student ID': r.student.student_id,
            'Name': f"{r.student.first_name} {r.student.last_name}",
            'Time': r.time.strftime('%H:%M'),
            'Course': r.course,
            'Status': r.status
        } for r in records]
        df = pd.DataFrame(data)
        filename = f"daily_report_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return self._export(df, filename, export_format)

    def _export(self, df, filename, fmt):
        path = EXPORTS_DIR / f"{filename}.{fmt}"
        if fmt == 'excel':
            df.to_excel(path, index=False)
        elif fmt == 'csv':
            df.to_csv(path, index=False)
        elif fmt == 'pdf':
            # Simple PDF using ReportLab
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            doc = SimpleDocTemplate(str(path), pagesize=A4)
            elements = []
            table_data = [df.columns.tolist()] + df.values.tolist()
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            elements.append(t)
            doc.build(elements)
        return str(path)