"""
cleanup_db.py — Tek seferlik veritabanı temizleme scripti.

Kullanım:
  Lokal (SQLite):  python cleanup_db.py
  Render (Postgres): DATABASE_URL ortam değişkeni .env'de tanımlıysa otomatik kullanılır.

Ne yapar:
  1. Measurements tablosundaki tüm kayıtları siler (FK bağımlılığı nedeniyle önce).
  2. Users tablosundaki tüm kayıtları siler.
  3. Silinen kayıt sayılarını raporlar.
  4. İşlemi onaylamadan başlamaz — yanlışlıkla çalıştırmaya karşı koruma sağlar.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# ── Veritabanı Bağlantısı ────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./diabetes_tracker.db"
    print(f"ℹ️  DATABASE_URL bulunamadı, lokal SQLite kullanılıyor: {DATABASE_URL}")
else:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print(f"ℹ️  Hedef veritabanı: {DATABASE_URL[:40]}...")

# ── Onay Kontrolü ────────────────────────────────────────────────────────────
print()
print("⚠️  DİKKAT: Bu işlem geri alınamaz!")
print("   Tüm users ve measurements kayıtları silinecek.")
print()
answer = input("Devam etmek için 'EVET' yazın: ").strip()

if answer != "EVET":
    print("❌ İptal edildi. Hiçbir kayıt silinmedi.")
    sys.exit(0)

# ── Temizleme ────────────────────────────────────────────────────────────────
engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    print()
    print("🗑️  Measurements tablosu temizleniyor...")
    result = conn.execute(text("DELETE FROM measurements"))
    deleted_measurements = result.rowcount
    print(f"   → {deleted_measurements} kayıt silindi.")

    print("🗑️  Users tablosu temizleniyor...")
    result = conn.execute(text("DELETE FROM users"))
    deleted_users = result.rowcount
    print(f"   → {deleted_users} kayıt silindi.")

print()
print("✅ Temizlik tamamlandı!")
print(f"   Silinen ölçüm : {deleted_measurements}")
print(f"   Silinen kullanıcı: {deleted_users}")
