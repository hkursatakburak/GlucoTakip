import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# .env dosyasındaki değişkenleri yükle
load_dotenv()

# Canlı veritabanı URL'sini al
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("HATA: DATABASE_URL bulunamadı. Lütfen işlemlere başlamadan önce .env dosyanıza Render veritabanı URL'nizi ekleyin.")
    exit(1)

# SQLAlchemy için URL düzeltmesi (Render bazen postgres:// verir, SQLAlchemy postgresql:// bekler)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"Bağlantı motoru oluşturulamadı: {e}")
    exit(1)

def apply_migration():
    print("Veritabanına bağlanılıyor...")
    try:
        with engine.connect() as conn:
            # Sütunları güvenli bir şekilde ekle (IF NOT EXISTS sayesinde varsa hata vermez)
            print("Sütunlar ekleniyor...")
            
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS data_consent BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;"))
            
            # Değişiklikleri kaydet
            conn.commit()
            print("✅ BAŞARILI: 'data_consent', 'is_verified' ve 'is_admin' sütunları 'users' tablosuna başarıyla eklendi!")
            print("Artık Render üzerindeki sisteminiz sorunsuz çalışacaktır.")
    except Exception as e:
        print(f"❌ HATA OLUŞTU: Sütunlar eklenirken bir sorun yaşandı.\nDetay: {e}")

if __name__ == "__main__":
    apply_migration()
