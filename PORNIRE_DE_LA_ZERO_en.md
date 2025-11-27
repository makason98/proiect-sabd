# Starting from Scratch - Student Management System (SABD)

Complete guide for setting up and running the project from zero on Ubuntu/Linux.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup (Docker)](#database-setup-docker)
3. [Python Environment Setup](#python-environment-setup)
4. [Starting the Application](#starting-the-application)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Quick Commands Cheatsheet](#quick-commands-cheatsheet)

---

## 1. Prerequisites

### Required Software:
- **Docker** (for SQL Server and CouchDB)
- **Python 3.10+**
- **Git** (optional, for cloning)

### Installation (Ubuntu/Debian):

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Verify installations
docker --version
python3 --version
```

---

## 2. Database Setup (Docker)

### A. SQL Server Container

```bash
docker run -d \
  --name sabd_sqlserver \
  -e 'ACCEPT_EULA=Y' \
  -e 'SA_PASSWORD=StrongPassword123!' \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest
```

**Verify SQL Server is running:**
```bash
docker ps | grep sabd_sqlserver
# Should show: STATUS: Up
```

### B. CouchDB Container

```bash
docker run -d \
  --name sabd_couchdb \
  -e COUCHDB_USER=admin \
  -e COUCHDB_PASSWORD=password \
  -p 5984:5984 \
  couchdb:3.3.3
```

**Verify CouchDB is running:**
```bash
curl http://admin:password@localhost:5984/
# Should return: {"couchdb":"Welcome",...}
```

---

## 3. Python Environment Setup

```bash
# Navigate to project directory
cd /home/tehnic/.gemini/antigravity/scratch/proiect-sabd

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi uvicorn sqlalchemy pymssql couchdb pydantic...
```

---

## 4. Starting the Application

```bash
# Make sure you're in the project directory with venv activated
source venv/bin/activate

# Start FastAPI server
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 5. Verification

### A. Test API (Swagger UI)

1. Open browser: http://127.0.0.1:8000/docs
2. You should see the interactive API documentation
3. Try creating a student:
   - Click `POST /students/`
   - Click "Try it out"
   - Enter JSON:
     ```json
     {
       "nume": "Doe",
       "prenume": "John",
       "email": "john.doe@example.com",
       "data_nasterii": "2000-01-15"
     }
     ```
   - Click "Execute"
   - Verify response: `200 OK`

### B. Check SQL Server

```bash
docker exec -it sabd_sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'StrongPassword123!' -C -Q "SELECT * FROM students"
```

### C. Check CouchDB

1. Open: http://localhost:5984/_utils
2. Login: admin / password
3. Navigate to `students_sync` database
4. Verify student document exists

---

## 6. Troubleshooting

### Issue 1: Port 1433/5984 already in use

```bash
# Find process using port
sudo lsof -i :1433
sudo lsof -i :5984

# Kill process or stop conflicting containers
docker stop $(docker ps -q --filter "expose=1433")
docker stop $(docker ps -q --filter "expose=5984")
```

### Issue 2: Port 8000 already in use

```bash
# Kill uvicorn processes
pkill -f uvicorn

# Or use different port
uvicorn main:app --reload --port 8001
```

### Issue 3: Docker containers not starting

```bash
# Check Docker daemon
sudo systemctl status docker

# Start Docker if stopped
sudo systemctl start docker

# View container logs
docker logs sabd_sqlserver
docker logs sabd_couchdb
```

### Issue 4: Python dependencies fail

```bash
# Make sure venv is activated
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Retry installation
pip install -r requirements.txt
```

### Issue 5: "externally-managed-environment" error

```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 7. Quick Commands Cheatsheet

### Start Everything

```bash
# 1. Start databases
docker start sabd_sqlserver sabd_couchdb

# 2. Activate Python environment
cd /home/tehnic/.gemini/antigravity/scratch/proiect-sabd
source venv/bin/activate

# 3. Start API
uvicorn main:app --reload
```

### Stop Everything

```bash
# Stop API: CTRL+C in terminal

# Stop databases
docker stop sabd_sqlserver sabd_couchdb
```

### Check Status

```bash
# Docker containers
docker ps

# API (in browser)
http://127.0.0.1:8000/docs

# CouchDB UI
http://localhost:5984/_utils
```

### Run Tests

```bash
source venv/bin/activate
python test_consistency.py
```

### Migrate Existing Data

```bash
source venv/bin/activate
python migrate_to_couchdb.py
```

---

## 📝 Important Notes

1. **First Run**: SQL tables are created automatically at startup
2. **CouchDB Database**: Created automatically (`students_sync`)
3. **Passwords**: 
   - SQL Server: `StrongPassword123!`
   - CouchDB: admin / password
4. **Data Persistence**: Docker volumes ensure data survives container restarts

---

## 🔗 Next Steps

- Read [RAPORT_TEHNIC_en.md](RAPORT_TEHNIC_en.md) for technical details
- Read [ARHITECTURA_en.md](ARHITECTURA_en.md) to understand the architecture
- Run automated tests: `python test_consistency.py`

