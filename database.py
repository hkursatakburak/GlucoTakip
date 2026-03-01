import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Render'dan veya .env'den gelen adresi al (Yoksa None döner)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render linkleri bazen postgres:// ile başlıyor.
    # SQLAlchemy 1.4+ sürümleri sadece postgresql:// (sonunda 'ql' var) formatını kabul eder.
    # Sorun yaşamamak için otomatik düzeltme yapıyoruz:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Render'daki (PostgreSQL) veritabanı motorunu oluştur
    engine = create_engine(DATABASE_URL)

else:
    # Lokal (Kendi bilgisayarımız) için varsayılan SQLite ayarı
    DATABASE_URL = "sqlite:///./diabetes_tracker.db"
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
