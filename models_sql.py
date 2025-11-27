from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from database_sql import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nume = Column(String(100), nullable=False)
    prenume = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    data_nasterii = Column(Date, nullable=False)

    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    nume_curs = Column(String(200), nullable=False)
    credite = Column(Integer, nullable=False)
    profesor = Column(String(100), nullable=True)

    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    curs_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    data_inrolare = Column(Date, nullable=False)
    nota = Column(Float, nullable=True)

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
