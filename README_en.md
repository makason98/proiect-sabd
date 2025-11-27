# Student Management System (Hybrid SQL + NoSQL)

REST API for data synchronization between SQL Server and CouchDB.

## 🚀 Quick Start

### Prerequisites
- Docker
- Python 3.10+

### Installation

1. **Clone/Navigate to project**
   ```bash
   cd /home/tehnic/.gemini/antigravity/scratch/proiect-sabd
   ```

2. **Start databases (Docker)**
   ```bash
   docker start sabd_sqlserver sabd_couchdb
   # Or create them if they don't exist (see PORNIRE_DE_LA_ZERO_en.md)
   ```

3. **Install Python dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Start API**
   ```bash
   uvicorn main:app --reload
   ```

5. **Access application**
   - API Docs: http://127.0.0.1:8000/docs
   - CouchDB UI: http://localhost:5984/_utils (admin/password)

## 📚 Documentation

- **[RAPORT_TEHNIC_en.md](RAPORT_TEHNIC_en.md)** - Complete technical report
- **[PORNIRE_DE_LA_ZERO_en.md](PORNIRE_DE_LA_ZERO_en.md)** - Detailed startup guide
- **[ARHITECTURA_en.md](ARHITECTURA_en.md)** - Architecture guide

## 🏗️ Architecture

```
Client → FastAPI → SQL Server (relational)
                 → CouchDB (NoSQL)
```

## 🔧 Technologies

- **Backend**: Python 3.12, FastAPI
- **SQL**: SQL Server 2022 (Microsoft)
- **NoSQL**: CouchDB 3.3.3 (Apache)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic

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

## 🧪 Testing

```bash
# Automated testing
python test_consistency.py

# Manual testing
# Access http://127.0.0.1:8000/docs
```

## 📊 Synchronization

All CRUD operations (Create, Read, Update, Delete) automatically synchronize data between SQL Server and CouchDB.

SQL Server = primary source of truth  
CouchDB = replica for backup/replication

## 🔗 Migrate Existing Data

If you have old data in SQL Server created before synchronization was implemented:

```bash
python migrate_to_couchdb.py
```

## 📄 License

Academic project - Advanced Database Systems (SABD)
