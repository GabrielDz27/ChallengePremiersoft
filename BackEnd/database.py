# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql://root:123456@localhost:3306/data_saude"

engine = create_engine("mysql+pymysql://root:123456@localhost:3306/data_saude", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
