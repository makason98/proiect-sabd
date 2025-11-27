"""
Script de migrare inițială: SQL Server → CouchDB

Rulează acest script DOAR o dată pentru a sincroniza datele existente
din SQL Server în CouchDB (date create înainte de implementarea sincronizării).

Rulare:
    python migrate_to_couchdb.py
"""

from database_sql import SessionLocal
import models_sql
import database_nosql

def migrate_students():
    """Migrează toți studenții din SQL în CouchDB"""
    db = SessionLocal()
    try:
        students = db.query(models_sql.Student).all()
        print(f"\n🔄 Migrare {len(students)} studenți...")
        
        for student in students:
            student_dict = {
                "id": student.id,
                "nume": student.nume,
                "prenume": student.prenume,
                "email": student.email,
                "data_nasterii": student.data_nasterii.isoformat() if student.data_nasterii else None
            }
            database_nosql.sync_student_to_couchdb(student_dict)
        
        print(f"✅ {len(students)} studenți sincronizați!")
    finally:
        db.close()

def migrate_courses():
    """Migrează toate cursurile din SQL în CouchDB"""
    db = SessionLocal()
    try:
        courses = db.query(models_sql.Course).all()
        print(f"\n🔄 Migrare {len(courses)} cursuri...")
        
        for course in courses:
            course_dict = {
                "id": course.id,
                "nume_curs": course.nume_curs,
                "credite": course.credite,
                "profesor": course.profesor
            }
            database_nosql.sync_course_to_couchdb(course_dict)
        
        print(f"✅ {len(courses)} cursuri sincronizate!")
    finally:
        db.close()

def migrate_enrollments():
    """Migrează toate înrolările din SQL în CouchDB"""
    db = SessionLocal()
    try:
        enrollments = db.query(models_sql.Enrollment).all()
        print(f"\n🔄 Migrare {len(enrollments)} înrolări...")
        
        for enrollment in enrollments:
            enrollment_dict = {
                "id": enrollment.id,
                "student_id": enrollment.student_id,
                "curs_id": enrollment.curs_id,
                "data_inrolare": enrollment.data_inrolare.isoformat() if enrollment.data_inrolare else None,
                "nota": enrollment.nota
            }
            database_nosql.sync_enrollment_to_couchdb(enrollment_dict)
        
        print(f"✅ {len(enrollments)} înrolări sincronizate!")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MIGRARE INIȚIALĂ SQL SERVER → COUCHDB")
    print("=" * 60)
    
    migrate_students()
    migrate_courses()
    migrate_enrollments()
    
    print("\n" + "=" * 60)
    print("✅ MIGRARE COMPLETĂ!")
    print("=" * 60)
    print("\nVerifică CouchDB: http://localhost:5984/_utils")
