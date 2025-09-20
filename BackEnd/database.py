# backend/database.py

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_CONNECTION_STRING = os.getenv("DATABASE_CONNECTION_STRING")

engine = create_engine(DATABASE_CONNECTION_STRING, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()