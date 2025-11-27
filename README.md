# Sistem Gestiune Studenți (Hibrid SQL + NoSQL)

API REST pentru sincronizarea datelor între SQL Server și CouchDB.

## 🚀 Pornire Rapidă

### Precondiții
- Docker
- Python 3.10+

### Instalare

1. **Clone/Navigate to project**
   ```bash
   cd /home/tehnic/.gemini/antigravity/scratch/proiect-sabd
   ```

2. **Pornire baze de date (Docker)**
   ```bash
   docker start sabd_sqlserver sabd_couchdb
   # Sau creează-le dacă nu există (vezi PORNIRE_DE_LA_ZERO.md)
   ```

3. **Instalare dependențe Python**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Pornire API**
   ```bash
   uvicorn main:app --reload
   ```

5. **Accesare aplicație**
   - API Docs: http://127.0.0.1:8000/docs
   - CouchDB UI: http://localhost:5984/_utils (admin/password)

## 📚 Documentație

- **[RAPORT_TEHNIC.md](RAPORT_TEHNIC.md)** - Raport tehnic complet
- **[PORNIRE_DE_LA_ZERO.md](PORNIRE_DE_LA_ZERO.md)** - Ghid detaliat de pornire

## 🏗️ Arhitectură

```
Client → FastAPI → SQL Server (relațional)
                 → CouchDB (NoSQL)
```

## 🔧 Tehnologii

- **Backend**: Python 3.12, FastAPI
- **SQL**: SQL Server 2022 (Microsoft)
- **NoSQL**: CouchDB 3.3.3 (Apache)
- **ORM**: SQLAlchemy
- **Validare**: Pydantic

## 📝 API Endpoints

### Students
- `POST /students/` - Create
- `GET /students/` - List all
- `GET /students/{id}` - Get by ID
- `PUT /students/{id}` - Update
- `DELETE /students/{id}` - Delete

### Courses
- `POST /courses/` - Create
- `GET /courses/` - List all
- `GET /courses/{id}` - Get by ID
- `PUT /courses/{id}` - Update
- `DELETE /courses/{id}` - Delete

### Enrollments
- `POST /enrollments/` - Create
- `GET /enrollments/` - List all
- `GET /enrollments/{id}` - Get by ID
- `PUT /enrollments/{id}` - Update
- `DELETE /enrollments/{id}` - Delete

## 🧪 Testare

```bash
# Testare automată
python test_consistency.py

# Testare manuală
# Accesează http://127.0.0.1:8000/docs
```

## 📊 Sincronizare

Toate operațiile CRUD (Create, Read, Update, Delete) sincronizează automat datele între SQL Server și CouchDB.

SQL Server = sursa principală de adevăr  
CouchDB = replică pentru backup/replicare

## 🔗 Migrare Date Existente

Dacă ai date vechi în SQL Server create înainte de implementarea sincronizării:

```bash
python migrate_to_couchdb.py
```

## 📄 Licență

Proiect academic - Sisteme Avansate de Baze de Date (SABD)
