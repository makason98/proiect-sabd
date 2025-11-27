from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import SQL_SERVER_CONNECTION_STRING

# Creare engine SQLAlchemy
# echo=True afișează query-urile SQL în consolă (util pentru debug)
engine = create_engine(SQL_SERVER_CONNECTION_STRING, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
