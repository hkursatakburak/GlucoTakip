"""
make_admin.py — Bir kullanıcıya admin yetkisi vermek için tek seferlik script.

Kullanım:
  python make_admin.py --email admin@example.com
  python make_admin.py --email admin@example.com --revoke   (admin'i geri al)
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./diabetes_tracker.db"
    print(f"ℹ️  DATABASE_URL bulunamadı, lokal SQLite kullanılıyor.")
else:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"ℹ️  Hedef: {DATABASE_URL[:40]}...")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    parser = argparse.ArgumentParser(description="GlucoTakip — Admin Yetkilendirme")
    parser.add_argument("--email", required=True, help="Admin yapılacak kullanıcının e-postası")
    parser.add_argument("--revoke", action="store_true", help="Admin yetkisini geri al")
    args = parser.parse_args()

    # models'i burada import ediyoruz (DATABASE_URL yüklendikten sonra)
    import models  # noqa: F401 — SQLAlchemy kayıt için gerekli

    db = SessionLocal()
    try:
        from models import User
        user = db.query(User).filter(User.email == args.email).first()
        if not user:
            print(f"❌ '{args.email}' e-postasına sahip kullanıcı bulunamadı.")
            sys.exit(1)

        if args.revoke:
            user.is_admin = False
            action = "Admin yetkisi KALDIRILDI"
        else:
            user.is_admin = True
            action = "Admin yetkisi VERİLDİ"

        db.commit()
        print(f"✅ {action}: {user.full_name} <{user.email}>")

    finally:
        db.close()

if __name__ == "__main__":
    main()
