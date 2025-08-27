from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Default to SQLite for local/simple deployments
    DATABASE_URL = "sqlite:///./riskradar.db"
    print(f"Using SQLite database: {DATABASE_URL}")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    print(f"Using PostgreSQL database")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session