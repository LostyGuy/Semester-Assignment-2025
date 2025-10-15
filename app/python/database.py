from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLLITE_DATABASE_URL = "sqlite:///my_db.db" 

engine = create_engine(SQLLITE_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit = False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()