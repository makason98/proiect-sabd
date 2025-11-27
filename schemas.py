from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

# --- Student Schemas ---
class StudentBase(BaseModel):
    nume: str
    prenume: str
    email: EmailStr
    data_nasterii: date

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Course Schemas ---
class CourseBase(BaseModel):
    nume_curs: str
    credite: int
    profesor: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int

    class Config:
        from_attributes = True

# --- Enrollment Schemas ---
class EnrollmentBase(BaseModel):
    student_id: int
    curs_id: int
    data_inrolare: date
    nota: Optional[float] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int

    class Config:
        from_attributes = True
