# Ghid: Pornire Proiect de la Zero (Ubuntu)

## Precondiții
- Docker instalat
- Python 3.12 (sau 3.10+)

---

## Pași de pornire (după ce ai închis tot)

### 1. Navighează în directorul proiectului
```bash
cd /home/tehnic/.gemini/antigravity/scratch/proiect-sabd
```

### 2. Pornește containerele Docker (Baze de Date)

#### Verifică dacă containerele există deja (oprit)
```bash
docker ps -a | grep sabd
```

#### Dacă există, pornește-le:
```bash
docker start sabd_sqlserver sabd_couchdb
```

#### Dacă NU există, creează-le manual:
```bash
# Creare rețea (doar prima dată)
docker network create sabd_network

# Pornire SQL Server
docker run -d \
  --name sabd_sqlserver \
  --network sabd_network \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=StrongPassword123!" \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest

# Pornire CouchDB
docker run -d \
  --name sabd_couchdb \
  --network sabd_network \
  -e "COUCHDB_USER=admin" \
  -e "COUCHDB_PASSWORD=password" \
  -p 5984:5984 \
  couchdb:3.3.3
```

#### Verifică dacă rulează:
```bash
docker ps
```
Ar trebui să vezi `sabd_sqlserver` și `sabd_couchdb` în listă.

---

### 3. Activează mediul virtual Python
```bash
source venv/bin/activate
```

**Notă**: Dacă vezi `(venv)` la începutul prompt-ului terminal, ești în mediul virtual.

---

### 4. Pornește API-ul FastAPI
```bash
uvicorn main:app --reload
```

**Output așteptat**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Accesare Aplicație

### API (Swagger UI)
Deschide în browser:
```
http://127.0.0.1:8000/docs
```

### CouchDB (Interfață Web)
```
http://localhost:5984/_utils
```
- **User**: admin
- **Password**: password

---

## Oprire Completă

### 1. Oprește API-ul
În terminalul unde rulează `uvicorn`, apasă:
```
CTRL + C
```

### 2. Oprește containerele Docker
```bash
docker stop sabd_sqlserver sabd_couchdb
```

### 3. (Opțional) Șterge containerele
**ATENȚIE**: Acest lucru șterge TOATE datele din baze!
```bash
docker rm sabd_sqlserver sabd_couchdb
docker network rm sabd_network
```

---

## Troubleshooting

### Container nu pornește: "port already in use"
```bash
# Vezi ce proces ocupă portul 1433
sudo lsof -i :1433

# Oprește containerul vechi
docker stop $(docker ps -q --filter "publish=1433")
```

### Eroare: "pyodbc not found" sau "Driver not found"
Proiectul folosește `pymssql` (nu `pyodbc`). Verifică `config.py`:
```python
SQL_SERVER_CONNECTION_STRING = "mssql+pymssql://sa:StrongPassword123!@localhost:1433/master"
```

### Regenerare mediu virtual (dacă lipsesc pachete)
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install email-validator  # necesar pentru Pydantic
pip install pymssql           # driver SQL Server
```

---

## Comenzi Rapide (Cheatsheet)

| Acțiune                     | Comandă                                      |
|-----------------------------|----------------------------------------------|
| Pornire containere          | `docker start sabd_sqlserver sabd_couchdb`   |
| Oprire containere           | `docker stop sabd_sqlserver sabd_couchdb`    |
| Vezi containere active      | `docker ps`                                  |
| Activare venv               | `source venv/bin/activate`                   |
| Pornire API                 | `uvicorn main:app --reload`                  |
| Swagger UI                  | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| CouchDB UI                  | [http://localhost:5984/_utils](http://localhost:5984/_utils) |
