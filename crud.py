from sqlalchemy.orm import Session
import models_sql
import schemas

# --- Student CRUD ---
def get_student(db: Session, student_id: int):
    return db.query(models_sql.Student).filter(models_sql.Student.id == student_id).first()

def get_student_by_email(db: Session, email: str):
    return db.query(models_sql.Student).filter(models_sql.Student.email == email).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models_sql.Student).order_by(models_sql.Student.id).offset(skip).limit(limit).all()

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models_sql.Student(
        nume=student.nume,
        prenume=student.prenume,
        email=student.email,
        data_nasterii=student.data_nasterii
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student: schemas.StudentCreate):
    db_student = db.query(models_sql.Student).filter(models_sql.Student.id == student_id).first()
    if db_student:
        db_student.nume = student.nume
        db_student.prenume = student.prenume
        db_student.email = student.email
        db_student.data_nasterii = student.data_nasterii
        db.commit()
        db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int):
    db_student = db.query(models_sql.Student).filter(models_sql.Student.id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
        return True
    return False

# --- Course CRUD ---
def get_course(db: Session, course_id: int):
    return db.query(models_sql.Course).filter(models_sql.Course.id == course_id).first()

def get_courses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models_sql.Course).order_by(models_sql.Course.id).offset(skip).limit(limit).all()

def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models_sql.Course(
        nume_curs=course.nume_curs,
        credite=course.credite,
        profesor=course.profesor
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_course(db: Session, course_id: int, course: schemas.CourseCreate):
    db_course = db.query(models_sql.Course).filter(models_sql.Course.id == course_id).first()
    if db_course:
        db_course.nume_curs = course.nume_curs
        db_course.credite = course.credite
        db_course.profesor = course.profesor
        db.commit()
        db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int):
    db_course = db.query(models_sql.Course).filter(models_sql.Course.id == course_id).first()
    if db_course:
        db.delete(db_course)
        db.commit()
        return True
    return False

# --- Enrollment CRUD ---
def create_enrollment(db: Session, enrollment: schemas.EnrollmentCreate):
    db_enrollment = models_sql.Enrollment(
        student_id=enrollment.student_id,
        curs_id=enrollment.curs_id,
        data_inrolare=enrollment.data_inrolare,
        nota=enrollment.nota
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

def update_enrollment(db: Session, enrollment_id: int, enrollment: schemas.EnrollmentCreate):
    db_enrollment = db.query(models_sql.Enrollment).filter(models_sql.Enrollment.id == enrollment_id).first()
    if db_enrollment:
        db_enrollment.student_id = enrollment.student_id
        db_enrollment.curs_id = enrollment.curs_id
        db_enrollment.data_inrolare = enrollment.data_inrolare
        db_enrollment.nota = enrollment.nota
        db.commit()
        db.refresh(db_enrollment)
    return db_enrollment

def delete_enrollment(db: Session, enrollment_id: int):
    db_enrollment = db.query(models_sql.Enrollment).filter(models_sql.Enrollment.id == enrollment_id).first()
    if db_enrollment:
        db.delete(db_enrollment)
        db.commit()
        return True
    return False

def get_enrollments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models_sql.Enrollment).order_by(models_sql.Enrollment.id).offset(skip).limit(limit).all()
