# backend/app/db.py
from sqlmodel import create_engine, SQLModel, Session
from pathlib import Path
from contextlib import contextmanager
from sqlmodel import Session


DB_FILE = Path(__file__).resolve().parents[1] / "db.sqlite3"
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)
from contextlib import contextmanager
from sqlmodel import Session

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

