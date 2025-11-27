# Architecture Guide - How the Project Works

## 📋 Table of Contents
1. [File Structure](#file-structure)
2. [Data Flow](#data-flow)
3. [How Components Are Connected](#how-components-are-connected)
4. [Execution Examples](#execution-examples)
5. [Why All These Files Are Necessary](#why-all-these-files-are-necessary)
6. [Complete Dependency Diagram](#complete-dependency-diagram)
7. [How to Explain the Project](#how-to-explain-the-project)

---

## 1. File Structure

```
proiect-sabd/
│
├── main.py                 # APPLICATION CORE - FastAPI API
├── config.py               # Database connection settings
├── models_sql.py           # SQL table structure (ORM)
├── schemas.py              # API data validation (Pydantic)
├── crud.py                 # CRUD logic for SQL
├── database_sql.py         # SQL Server connection
├── database_nosql.py       # CouchDB connection + sync
├── requirements.txt        # Required Python libraries
├── docker-compose.yml      # Docker container configuration
├── README.md               # Quick start
├── RAPORT_TEHNIC.md        # Complete technical report
└── migrate_to_couchdb.py   # Existing data migration script
```

### Role of Each File:

| File | What It Does | Why It's Important |
|------|-------------|-------------------|
| `main.py` | Defines API endpoints | **PROJECT CENTER** - all requests arrive here |
| `config.py` | Stores connection URLs | Change here if you change server/password |
| `models_sql.py` | Defines SQL tables | SQLAlchemy uses this to create/read from tables |
| `schemas.py` | Validates received JSON | Pydantic automatically checks data before DB |
| `crud.py` | Database operations | Functions that actually INSERT/SELECT/UPDATE/DELETE |
| `database_sql.py` | SQL connection config | Creates SQLAlchemy "engine" |
| `database_nosql.py` | CouchDB sync | Functions to send data to CouchDB |

---

## 2. Data Flow (Step by Step)

### Example: Creating a Student

```mermaid
sequenceDiagram
    participant Browser
    participant FastAPI
    participant Pydantic
    participant CRUD
    participant SQL
    participant CouchDB

    Browser->>FastAPI: POST /students/ {"nume": "Ion", ...}
    FastAPI->>Pydantic: Validate data (schemas.StudentCreate)
    
    alt Invalid data
        Pydantic-->>Browser: 422 Validation Error
    else Valid data
        Pydantic->>CRUD: crud.create_student()
        CRUD->>SQL: INSERT INTO students ...
        SQL-->>CRUD: ID=1 (student created)
        CRUD->>CouchDB: sync_student_to_couchdb(student_dict)
        CouchDB-->>CRUD: Document saved
        CRUD-->>Browser: 200 OK {"id": 1, "nume": "Ion", ...}
    end
```

### Step by Step (Explained):

1. **Browser sends request**: `POST http://127.0.0.1:8000/students/`
2. **FastAPI (main.py)** receives request at `create_student()` function
3. **Pydantic (schemas.py)** validates data:
   - Valid email? ✅
   - Birth date in correct format? ✅
   - All required fields? ✅
4. **CRUD (crud.py)** receives validated object and:
   - Creates SQLAlchemy object (`models_sql.Student`)
   - Does `db.add()` and `db.commit()` → Save to SQL Server
5. **CouchDB Synchronization**:
   - Converts SQL object to Python dictionary
   - Calls `sync_student_to_couchdb()` from `database_nosql.py`
   - CouchDB receives and saves JSON document
6. **Response back**: FastAPI returns JSON with created student

---

## 3. How Components Are Connected

### A. FastAPI + Swagger UI

```python
# main.py
from fastapi import FastAPI

app = FastAPI(
    title="Student Management System",  # ← Appears in Swagger UI
    description="...",                   # ← Description in UI
)

@app.post("/students/")  # ← Becomes green button in Swagger
def create_student(...):
    ...
```

**How does Swagger UI appear?**
- FastAPI reads all decorators `@app.get()`, `@app.post()`, etc.
- Automatically generates JSON (OpenAPI spec) at `/openapi.json`
- Serves Swagger interface at `/docs` (HTML/CSS/JS embedded in FastAPI library)

**You don't have any HTML files** - everything is auto-generated!

---

### B. FastAPI + SQLAlchemy (SQL Server)

```python
# 1. Connection configuration (database_sql.py)
from sqlalchemy import create_engine
engine = create_engine(SQL_SERVER_CONNECTION_STRING)
SessionLocal = sessionmaker(bind=engine)

# 2. Define models (models_sql.py)
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    nume = Column(String(100))

# 3. Create tables (main.py - at startup)
models_sql.Base.metadata.create_all(bind=engine)

# 4. Use in endpoint (main.py)
@app.post("/students/")
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    #                                               ^^^^^^^^^^^^^^^^^^
    #                                               Dependency Injection!
    crud.create_student(db=db, student=student)
```

**Dependency Injection (`Depends(get_db)`):**
- FastAPI automatically calls `get_db()` which creates a SQL session
- Session is passed to the function
- At the end, session automatically closes

---

### C. FastAPI + CouchDB

```python
# 1. Connection (database_nosql.py)
import couchdb
server = couchdb.Server("http://admin:password@localhost:5984/")
db = server["students_sync"]

# 2. Save document
def sync_student_to_couchdb(student_data: dict):
    doc_id = f"student_{student_data['id']}"
    student_data['_id'] = doc_id
    db.save(student_data)

# 3. Call from endpoint (main.py)
@app.post("/students/")
def create_student(...):
    created_student = crud.create_student(...)
    
    # Convert to dict for CouchDB
    student_dict = {
        "id": created_student.id,
        "nume": created_student.nume,
        ...
    }
    database_nosql.sync_student_to_couchdb(student_dict)
```

---

## 4. Complete Dependency Diagram

```
Browser
   ↓
FastAPI (main.py) ────┬──→ Pydantic (schemas.py) → Validation
   ↓                  │
   ↓                  └──→ CORS Middleware → Security
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

## 5. Why All These Files Are Necessary?

| Question | Answer |
|----------|--------|
| **Why `schemas.py` when we have `models_sql.py`?** | `models_sql.py` = database structure (SQL)<br>`schemas.py` = API structure (JSON)<br>They're different because API doesn't expose ID at creation! |
| **Why `crud.py` separate from `main.py`?** | Separation of concerns:<br>- `main.py` = Routing and HTTP<br>- `crud.py` = Database logic<br>You can reuse CRUD functions elsewhere (scripts, console) |
| **Why two databases?** | Project requirement: demonstrate SQL + NoSQL integration<br>- SQL Server = Structured data, relationships, integrity<br>- CouchDB = Replication, flexibility, document-oriented |

---

## 6. How to Explain the Project (Presentation)

### Introduction (30 sec)
> "I created a REST API that automatically synchronizes data between a relational database (SQL Server) and a NoSQL one (CouchDB). The API is built with FastAPI, a modern Python framework."

### Architecture (1 min)
> "The application is divided into layers:
> - **API Layer** (main.py): Receives HTTP requests
> - **Validation Layer** (schemas.py): Automatic validation with Pydantic
> - **Business Logic** (crud.py): CRUD operations
> - **Data Layer**: SQL Server for relational data + CouchDB for replication"

### Synchronization (1 min)
> "With every CREATE, UPDATE, DELETE operation in SQL Server, the system automatically synchronizes data to CouchDB. I also implemented CASCADE DELETE - when you delete a student, their enrollments are automatically deleted."

### Security (30 sec)
> "I implemented CORS with origin whitelist to protect the API against CSRF attacks. Only approved applications can make requests."

### Demo (2 min)
> "I'll show you Swagger UI - the interface automatically generated by FastAPI. We'll create a student, update them, and verify that data is synchronized in both databases."

---

**Now you understand exactly how everything works! 🚀**
