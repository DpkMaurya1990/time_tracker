from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
import os




# SQLite database file create hogi 'work_tracker.db' naam se
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Engine create kar rahe hain jo DB se baat karega
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal class se hum har request ke liye naya DB session kholenge
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class jise use karke hum Tables (Models) banayenge
Base = declarative_base()

# Table definition
class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)  # 'START', 'PAUSE', 'RESUME', 'STOP'
    timestamp = Column(DateTime, default=datetime.now)
    source = Column(String, default="manual") # 'manual' ya 'idle_system'

# DB session get karne ka function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()