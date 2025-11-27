from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models_sql
import schemas
import crud
import database_nosql
from database_sql import engine, get_db

# Creare tabele în baza de date SQL la pornire
models_sql.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistem Gestiune Studenți (Hibrid SQL + NoSQL)",
    description="API pentru sincronizarea datelor între SQL Server și CouchDB",
    version="1.0.0"
)

# ===== SECURITATE: CORS Middleware =====
# Whitelist de origini permise (URL-uri care pot accesa API-ul)
allowed_origins = [
    "http://localhost:3000",      # Frontend local (React/Vue/Angular)
    "http://127.0.0.1:8000",      # Swagger UI (pentru testare)
    "http://localhost:8000",      # Swagger UI (alternativ)
    # Adaugă aici URL-ul tău de producție
    # "https://your-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Doar aceste URL-uri pot face request-uri
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Metode HTTP permise
    allow_headers=["*"],  # Header-e permise
)

@app.get("/")
def read_root():
    return {"message": "Salut! API-ul este funcțional.", "docs": "/docs"}

# --- Students Endpoints ---
@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = crud.get_student_by_email(db, email=student.email)
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 1. Salvare în SQL Server
    created_student = crud.create_student(db=db, student=student)
    
    # 2. Sincronizare în CouchDB
    # Convertim obiectul SQLAlchemy în dict pentru CouchDB
    student_dict = {
        "id": created_student.id,
        "nume": created_student.nume,
        "prenume": created_student.prenume,
        "email": created_student.email,
        "data_nasterii": created_student.data_nasterii.isoformat() if created_student.data_nasterii else None
    }
    database_nosql.sync_student_to_couchdb(student_dict)
    
    return created_student

@app.get("/students/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students

@app.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # 1. Actualizare în SQL Server
    db_student = crud.update_student(db=db, student_id=student_id, student=student)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 2. Sincronizare în CouchDB
    student_dict = {
        "id": db_student.id,
        "nume": db_student.nume,
        "prenume": db_student.prenume,
        "email": db_student.email,
        "data_nasterii": db_student.data_nasterii.isoformat() if db_student.data_nasterii else None
    }
    database_nosql.sync_student_to_couchdb(student_dict)
    
    return db_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    # 1. Ștergere din SQL Server
    success = crud.delete_student(db=db, student_id=student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # 2. Ștergere din CouchDB
    couch_db = database_nosql.get_couchdb_db()
    if couch_db:
        doc_id = f"student_{student_id}"
        if doc_id in couch_db:
            doc = couch_db[doc_id]
            couch_db.delete(doc)
    
    return {"message": "Student deleted successfully"}

# --- Courses Endpoints ---
@app.post("/courses/", response_model=schemas.Course)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    # 1. Salvare în SQL Server
    created_course = crud.create_course(db=db, course=course)
    
    # 2. Sincronizare în CouchDB
    course_dict = {
        "id": created_course.id,
        "nume_curs": created_course.nume_curs,
        "credite": created_course.credite,
        "profesor": created_course.profesor
    }
    database_nosql.sync_course_to_couchdb(course_dict)
    
    return created_course

@app.get("/courses/", response_model=List[schemas.Course])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_courses(db, skip=skip, limit=limit)

@app.get("/courses/{course_id}", response_model=schemas.Course)
def read_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course

@app.put("/courses/{course_id}", response_model=schemas.Course)
def update_course(course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    # 1. Actualizare în SQL Server
    db_course = crud.update_course(db=db, course_id=course_id, course=course)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 2. Sincronizare în CouchDB
    course_dict = {
        "id": db_course.id,
        "nume_curs": db_course.nume_curs,
        "credite": db_course.credite,
        "profesor": db_course.profesor
    }
    database_nosql.sync_course_to_couchdb(course_dict)
    
    return db_course

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    # 1. Ștergere din SQL Server
    success = crud.delete_course(db=db, course_id=course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # 2. Ștergere din CouchDB
    couch_db = database_nosql.get_couchdb_db()
    if couch_db:
        doc_id = f"course_{course_id}"
        if doc_id in couch_db:
            doc = couch_db[doc_id]
            couch_db.delete(doc)
    
    return {"message": "Course deleted successfully"}

# --- Enrollments Endpoints ---
@app.post("/enrollments/", response_model=schemas.Enrollment)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    # 1. Salvare în SQL Server
    created_enrollment = crud.create_enrollment(db=db, enrollment=enrollment)
    
    # 2. Sincronizare în CouchDB
    enrollment_dict = {
        "id": created_enrollment.id,
        "student_id": created_enrollment.student_id,
        "curs_id": created_enrollment.curs_id,
        "data_inrolare": created_enrollment.data_inrolare.isoformat() if created_enrollment.data_inrolare else None,
        "nota": created_enrollment.nota
    }
    database_nosql.sync_enrollment_to_couchdb(enrollment_dict)
    
    return created_enrollment

@app.get("/enrollments/", response_model=List[schemas.Enrollment])
def read_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_enrollments(db, skip=skip, limit=limit)

@app.get("/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
def read_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = db.query(models_sql.Enrollment).filter(models_sql.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return db_enrollment

@app.put("/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
def update_enrollment(enrollment_id: int, enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    # 1. Actualizare în SQL Server
    db_enrollment = crud.update_enrollment(db=db, enrollment_id=enrollment_id, enrollment=enrollment)
    if db_enrollment is None:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # 2. Sincronizare în CouchDB
    enrollment_dict = {
        "id": db_enrollment.id,
        "student_id": db_enrollment.student_id,
        "curs_id": db_enrollment.curs_id,
        "data_inrolare": db_enrollment.data_inrolare.isoformat() if db_enrollment.data_inrolare else None,
        "nota": db_enrollment.nota
    }
    database_nosql.sync_enrollment_to_couchdb(enrollment_dict)
    
    return db_enrollment

@app.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    # 1. Ștergere din SQL Server
    success = crud.delete_enrollment(db=db, enrollment_id=enrollment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # 2. Ștergere din CouchDB
    couch_db = database_nosql.get_couchdb_db()
    if couch_db:
        doc_id = f"enrollment_{enrollment_id}"
        if doc_id in couch_db:
            doc = couch_db[doc_id]
            couch_db.delete(doc)
    
    return {"message": "Enrollment deleted successfully"}
