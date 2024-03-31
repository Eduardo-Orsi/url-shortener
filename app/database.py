from typing import Generator, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from .config import get_settings

engine = create_engine(get_settings().db_url)
Base = declarative_base()
session = sessionmaker(bind=engine)

def get_db() -> Generator[Session, Any, None]:
    db = session()
    try:
        yield db
    finally:
        db.close()
