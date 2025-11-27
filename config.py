# Setări pentru conexiunile la bazele de date

# SQL Server Config
# Folosim 'localhost' pentru că rulăm aplicația de pe host, nu din container
# Folosim pymssql ca driver (nu necesită instalare sistem)
SQL_SERVER_CONNECTION_STRING = "mssql+pymssql://sa:StrongPassword123!@localhost:1433/master"

# CouchDB Config
COUCHDB_URL = "http://admin:password@localhost:5984/"
COUCHDB_DB_NAME = "students_sync"
