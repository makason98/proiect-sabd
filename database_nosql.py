import couchdb
from config import COUCHDB_URL, COUCHDB_DB_NAME

def get_couchdb_server():
    try:
        server = couchdb.Server(COUCHDB_URL)
        return server
    except Exception as e:
        print(f"Eroare conectare CouchDB: {e}")
        return None

def get_couchdb_db():
    server = get_couchdb_server()
    if server:
        if COUCHDB_DB_NAME in server:
            return server[COUCHDB_DB_NAME]
        else:
            # Creăm baza de date dacă nu există
            try:
                return server.create(COUCHDB_DB_NAME)
            except Exception as e:
                print(f"Eroare creare baza de date CouchDB: {e}")
                return None
    return None

def sync_student_to_couchdb(student_data: dict):
    """
    Sincronizează datele unui student în CouchDB.
    student_data trebuie să fie un dicționar cu datele studentului.
    """
    db = get_couchdb_db()
    if db is None:
        print("Nu s-a putut conecta la CouchDB pentru sincronizare.")
        return

    # Folosim email-ul ca ID unic sau generăm unul bazat pe ID-ul SQL
    doc_id = f"student_{student_data.get('id')}"
    
    # Verificăm dacă documentul există deja
    if doc_id in db:
        doc = db[doc_id]
        # Actualizăm câmpurile
        doc.update(student_data)
        doc['type'] = 'student' # Marker pentru tipul documentului
        db.save(doc)
        print(f"Student {doc_id} actualizat în CouchDB.")
    else:
        # Creăm un document nou
        student_data['_id'] = doc_id
        student_data['type'] = 'student'
        db.save(student_data)
        print(f"Student {doc_id} creat în CouchDB.")

def sync_course_to_couchdb(course_data: dict):
    """
    Sincronizează datele unui curs în CouchDB.
    course_data trebuie să fie un dicționar cu datele cursului.
    """
    db = get_couchdb_db()
    if db is None:
        print("Nu s-a putut conecta la CouchDB pentru sincronizare.")
        return

    doc_id = f"course_{course_data.get('id')}"
    
    if doc_id in db:
        doc = db[doc_id]
        doc.update(course_data)
        doc['type'] = 'course'
        db.save(doc)
        print(f"Course {doc_id} actualizat în CouchDB.")
    else:
        course_data['_id'] = doc_id
        course_data['type'] = 'course'
        db.save(course_data)
        print(f"Course {doc_id} creat în CouchDB.")

def sync_enrollment_to_couchdb(enrollment_data: dict):
    """
    Sincronizează datele unei înrolări în CouchDB.
    enrollment_data trebuie să fie un dicționar cu datele înrolării.
    """
    db = get_couchdb_db()
    if db is None:
        print("Nu s-a putut conecta la CouchDB pentru sincronizare.")
        return

    doc_id = f"enrollment_{enrollment_data.get('id')}"
    
    if doc_id in db:
        doc = db[doc_id]
        doc.update(enrollment_data)
        doc['type'] = 'enrollment'
        db.save(doc)
        print(f"Enrollment {doc_id} actualizat în CouchDB.")
    else:
        enrollment_data['_id'] = doc_id
        enrollment_data['type'] = 'enrollment'
        db.save(enrollment_data)
        print(f"Enrollment {doc_id} creat în CouchDB.")
