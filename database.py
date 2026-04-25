from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

DATABASE_URL = "sqlite:///./stock_accounting.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化資料庫"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """取得資料庫連線"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
