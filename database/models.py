from sqlalchemy import Column, Integer, String, Date, Time, DateTime, LargeBinary, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    role = Column(String(20), default='admin')
    created_at = Column(DateTime, default=datetime.utcnow)

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    department = Column(String(100))
    course = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    gender = Column(String(10))
    photo_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    embeddings = relationship('Embedding', back_populates='student', cascade='all, delete-orphan')
    attendances = relationship('Attendance', back_populates='student', cascade='all, delete-orphan')

class Embedding(Base):
    __tablename__ = 'embeddings'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    embedding = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship('Student', back_populates='embeddings')

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    course = Column(String(100), nullable=False)
    status = Column(String(20), default='Present')  # Present, Absent, Late, Excused
    timestamp = Column(DateTime, default=datetime.utcnow)

    student = relationship('Student', back_populates='attendances')

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50))
    description = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__ = 'settings'
    key = Column(String(50), primary_key=True)
    value = Column(String(255))