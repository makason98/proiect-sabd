# Ghid de Arhitectură - Cum Funcționează Proiectul

## 📋 Cuprins
1. [Structura Fișierelor](#structura-fișierelor)
2. [Fluxul de Date](#fluxul-de-date)
3. [Cum Sunt Conectate Componentele](#cum-sunt-conectate-componentele)
4. [Exemple de Execuție](#exemple-de-execuție)

---

## 1. Structura Fișierelor

```
proiect-sabd/
│
├── main.py                 # INIMA APLICAȚIEI - API-ul FastAPI
├── config.py               # Configurări conexiuni baze de date
├── models_sql.py           # Structura tabelelor SQL (ORM)
├── schemas.py              # Validare date API (Pydantic)
├── crud.py                 # Logica CRUD pentru SQL
├── database_sql.py         # Conexiune la SQL Server
├── database_nosql.py       # Conexiune + sincronizare CouchDB
├── requirements.txt        # Biblioteci Python necesare
├── docker-compose.yml      # Configurare containere Docker
├── README.md               # Quick start
├── RAPORT_TEHNIC.md        # Raport tehnic complet
└── migrate_to_couchdb.py   # Script migrare date existente
```

### Rolul Fiecărui Fișier:

| Fișier | Ce Face | De Ce Este Important |
|--------|---------|----------------------|
| `main.py` | Definește endpoint-urile API | **CENTRUL PROIECTULUI** - aici ajung toate request-urile |
| `config.py` | Stochează URL-uri conectare | Schimbi aici dacă schimbi serverul/parola |
| `models_sql.py` | Definește tabele SQL | SQLAlchemy folosește asta pentru a crea/citi din tabele |
| `schemas.py` | Validează JSON-ul primit | Pydantic verifică automat datele înainte să ajungă în BD |
| `crud.py` | Operații bază de date | Funcțiile care chiar INSERT/SELECT/UPDATE/DELETE |
| `database_sql.py` | Configurare conexiune SQL | Creează "engine-ul" SQLAlchemy |
| `database_nosql.py` | Sincronizare CouchDB | Funcții de trimis date în CouchDB |

---

## 2. Fluxul de Date (Pas cu Pas)

### Exemplu: Crearea unui Student

```mermaid
sequenceDiagram
    participant Browser
    participant FastAPI
    participant Pydantic
    participant CRUD
    participant SQL
    participant CouchDB

    Browser->>FastAPI: POST /students/ {"nume": "Ion", ...}
    FastAPI->>Pydantic: Validează datele (schemas.StudentCreate)
    
    alt Date invalide
        Pydantic-->>Browser: 422 Validation Error
    else Date valide
        Pydantic->>CRUD: crud.create_student()
        CRUD->>SQL: INSERT INTO students ...
        SQL-->>CRUD: ID=1 (student creat)
        CRUD->>CouchDB: sync_student_to_couchdb(student_dict)
        CouchDB-->>CRUD: Document salvat
        CRUD-->>Browser: 200 OK {"id": 1, "nume": "Ion", ...}
    end
```

### Pas cu Pas (Explicat):

1. **Browser trimite request**: `POST http://127.0.0.1:8000/students/`
2. **FastAPI (main.py)** primește request-ul la funcția `create_student()`
3. **Pydantic (schemas.py)** validează datele:
   - Email valid? ✅
   - Data de naștere în format corect? ✅
   - Toate câmpurile obligatorii? ✅
4. **CRUD (crud.py)** primește obiectul validat și:
   - Creează obiect SQLAlchemy (`models_sql.Student`)
   - Face `db.add()` și `db.commit()` → Salvare în SQL Server
5. **Sincronizare CouchDB**:
   - Convertește obiectul SQL în dicționar Python
   - Apelează `sync_student_to_couchdb()` din `database_nosql.py`
   - CouchDB primește și salvează documentul JSON
6. **Răspuns înapoi**: FastAPI returnează JSON cu studentul creat

---

## 3. Cum Sunt Conectate Componentele

### A. FastAPI + Swagger UI

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="Sistem Gestiune Studenți",  # ← Apare în Swagger UI
    description="...",                  # ← Descrierea din UI
)

@app.post("/students/")  # ← Devine buton verde în Swagger
def create_student(...):
    ...
```

**Cum apare Swagger UI?**
- FastAPI citește toate decoratorii `@app.get()`, `@app.post()`, etc.
- Generează automat JSON (OpenAPI spec) la `/openapi.json`
- Servește interfața Swagger la `/docs` (HTML/CSS/JS încorporat în biblioteca FastAPI)

**Nu ai niciun fișier HTML** - totul este generat automat!

---

### B. FastAPI + SQLAlchemy (SQL Server)

```python
# 1. Configurare conexiune (database_sql.py)
from sqlalchemy import create_engine
engine = create_engine(SQL_SERVER_CONNECTION_STRING)
SessionLocal = sessionmaker(bind=engine)

# 2. Definire modele (models_sql.py)
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    nume = Column(String(100))

# 3. Creare tabele (main.py - la pornire)
models_sql.Base.metadata.create_all(bind=engine)

# 4. Folosire în endpoint (main.py)
@app.post("/students/")
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    #                                               ^^^^^^^^^^^^^^^^^^
    #                                               Dependency Injection!
    crud.create_student(db=db, student=student)
```

**Dependency Injection (`Depends(get_db)`):**
- FastAPI apelează automat `get_db()` care creează o sesiune SQL
- Sesiunea este pasată la funcție
- La final, sesiunea se închide automat

---

### C. FastAPI + CouchDB

```python
# 1. Conectare (database_nosql.py)
import couchdb
server = couchdb.Server("http://admin:password@localhost:5984/")
db = server["students_sync"]

# 2. Salvare document
def sync_student_to_couchdb(student_data: dict):
    doc_id = f"student_{student_data['id']}"
    student_data['_id'] = doc_id
    db.save(student_data)

# 3. Apelare din endpoint (main.py)
@app.post("/students/")
def create_student(...):
    created_student = crud.create_student(...)
    
    # Convertim în dict pentru CouchDB
    student_dict = {
        "id": created_student.id,
        "nume": created_student.nume,
        ...
    }
    database_nosql.sync_student_to_couchdb(student_dict)
```

**La ce folosește `.isoformat()`?**
```python
"data_nasterii": created_student.data_nasterii.isoformat()
# Convertește: date(2000, 1, 15) → "2000-01-15"
# CouchDB înțelege doar string-uri, nu obiecte Python date
```

---

### D. Pydantic + FastAPI (Validare)

```python
# 1. Definire schema (schemas.py)
from pydantic import BaseModel, EmailStr

class StudentCreate(BaseModel):
    nume: str
    prenume: str
    email: EmailStr  # ← Validare automată email
    data_nasterii: date

# 2. Folosire în endpoint (main.py)
@app.post("/students/")
def create_student(student: schemas.StudentCreate):
    #                        ^^^^^^^^^^^^^^^^^^^
    #                        Pydantic validează automat!
    # Dacă email invalid → HTTP 422 înainte să ajungă aici
```

**Validări automate:**
- `EmailStr` → Verifică format email valid
- `date` → Verifică format dată (YYYY-MM-DD)
- `str`, `int` → Verifică tipul
- Câmpuri lipsă → Eroare automată

---

## 4. Exemple de Execuție

### Exemplu 1: POST /students/ (Creare)

**Request:**
```http
POST http://127.0.0.1:8000/students/
Content-Type: application/json

{
  "nume": "Popescu",
  "prenume": "Ion",
  "email": "ion@example.com",
  "data_nasterii": "2000-01-15"
}
```

**Ce se întâmplă în cod:**

```python
# 1. FastAPI primește request-ul
@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    
    # 2. Pydantic a validat deja datele aici ✅
    
    # 3. Verificăm dacă email-ul există
    db_student = crud.get_student_by_email(db, email=student.email)
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 4. Salvare în SQL Server
    created_student = crud.create_student(db=db, student=student)
    # → SQL: INSERT INTO students (nume, prenume, email, data_nasterii) VALUES (...)
    
    # 5. Sincronizare în CouchDB
    student_dict = {
        "id": created_student.id,        # 1
        "nume": created_student.nume,    # "Popescu"
        "prenume": created_student.prenume,  # "Ion"
        "email": created_student.email,  # "ion@example.com"
        "data_nasterii": created_student.data_nasterii.isoformat()  # "2000-01-15"
    }
    database_nosql.sync_student_to_couchdb(student_dict)
    # → CouchDB: PUT /students_sync/student_1 {...}
    
    # 6. Returnare răspuns
    return created_student  # FastAPI convertește în JSON automat
```

**Rezultat în SQL Server:**
```sql
SELECT * FROM students WHERE id=1;
-- | id | nume    | prenume | email            | data_nasterii |
-- | 1  | Popescu | Ion     | ion@example.com  | 2000-01-15    |
```

**Rezultat în CouchDB:**
```json
{
  "_id": "student_1",
  "_rev": "1-abc123",
  "type": "student",
  "id": 1,
  "nume": "Popescu",
  "prenume": "Ion",
  "email": "ion@example.com",
  "data_nasterii": "2000-01-15"
}
```

---

### Exemplu 2: GET /students/ (Listare)

**Request:**
```http
GET http://127.0.0.1:8000/students/?skip=0&limit=10
```

**Ce se întâmplă:**

```python
@app.get("/students/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    # → SQL: SELECT * FROM students ORDER BY id OFFSET 0 LIMIT 10;
    
    return students
    # FastAPI convertește lista de obiecte SQLAlchemy în JSON automat
```

**Nu se sincronizează în CouchDB pentru READ** - doar citim din SQL.

---

## 5. De Ce Sunt Necesare Toate Aceste Fișiere?

| Întrebare | Răspuns |
|-----------|---------|
| **De ce `schemas.py` când am `models_sql.py`?** | `models_sql.py` = structura din baza de date (SQL)<br>`schemas.py` = structura din API (JSON)<br>Sunt diferite pentru că API-ul nu expune ID-ul la creare! |
| **De ce `crud.py` separat de `main.py`?** | Separarea responsabilităților:<br>- `main.py` = Routing și HTTP<br>- `crud.py` = Logică bază de date<br>Poți refolosi funcțiile CRUD în alte părți (scripturi, console) |
| **De ce două baze de date?** | Cerința proiectului: demonstrare integrare SQL + NoSQL<br>- SQL Server = Date structurate, relații, integritate<br>- CouchDB = Replicare, flexibilitate, document-oriented |

---

## 6. Diagrama Completă de Dependențe

```
Browser
   ↓
FastAPI (main.py) ────┬──→ Pydantic (schemas.py) → Validare
   ↓                  │
   ↓                  └──→ CORS Middleware → Securitate
   ↓
CRUD (crud.py) ───────┬──→ SQLAlchemy ORM (models_sql.py)
   ↓                  │         ↓
   ↓                  │    SQL Server (Docker)
   ↓                  │
   ↓                  └──→ CouchDB Client (database_nosql.py)
   ↓                           ↓
   ↓                      CouchDB (Docker)
   ↓
Response JSON
```

---

## 7. Cum Să Explici Proiectul (Prezentare)

### Introducere (30 sec)
> "Am creat un API REST care sincronizează automat datele între o bază relațională (SQL Server) și una NoSQL (CouchDB). API-ul este construit cu FastAPI, un framework Python modern."

### Arhitectura (1 min)
> "Aplicația este împărțită în layere:
> - **API Layer** (main.py): Primește request-uri HTTP
> - **Validation Layer** (schemas.py): Validare automată cu Pydantic
> - **Business Logic** (crud.py): Operații CRUD
> - **Data Layer**: SQL Server pentru date relaționale + CouchDB pentru replicare"

### Sincronizare (1 min)
> "La fiecare operație CREATE, UPDATE, DELETE în SQL Server, sistemul sincronizează automat datele în CouchDB. Am implementat și CASCADE DELETE - când ștergi un student, se șterg automat și înrolările lui."

### Securitate (30 sec)
> "Am implementat CORS cu whitelist de origini pentru a proteja API-ul împotriva atacurilor CSRF. Doar aplicațiile aprobate pot face request-uri."

### Demo (2 min)
> "Vă arăt Swagger UI - interfața generată automat de FastAPI. Vom crea un student, îl vom actualiza, și vom verifica că datele sunt sincronizate în ambele baze de date."

---

**Acum înțelegi exact cum funcționează totul! 🚀**
