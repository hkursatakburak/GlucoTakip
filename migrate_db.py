import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker
from models import Base

OLD_DB_URL = "postgresql://hkursat:L0py8Hdkwun5WzMnKHS1AgZ44jyORKH9@dpg-d6ic928gjchc73d8pcmg-a.frankfurt-postgres.render.com/glucotakip"
NEW_DB_URL = "postgresql://neondb_owner:npg_7CFsDeq3vgKQ@ep-polished-glade-alg4cs2d-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def migrate():
    print("Migrasyon başlıyor...")
    
    old_engine = create_engine(OLD_DB_URL)
    new_engine = create_engine(NEW_DB_URL)
    
    print("Yeni veritabanında tablolar oluşturuluyor (Base.metadata.create_all)...")
    Base.metadata.create_all(bind=new_engine)
    print("Tablolar başarıyla oluşturuldu.")
    
    old_meta = MetaData()
    old_meta.reflect(bind=old_engine)
    
    new_meta = MetaData()
    new_meta.reflect(bind=new_engine)
    
    with old_engine.connect() as old_conn:
        with new_engine.begin() as new_conn:
            for table in Base.metadata.sorted_tables:
                print(f"'{table.name}' tablosu taşınıyor...")
                
                old_table = old_meta.tables.get(table.name)
                if old_table is None:
                    print(f"'{table.name}' eski veritabanında bulunamadı, atlanıyor.")
                    continue
                
                new_table = new_meta.tables.get(table.name)
                if new_table is None:
                    print(f"'{table.name}' yeni veritabanında bulunamadı, atlanıyor.")
                    continue

                result = old_conn.execute(old_table.select())
                rows = result.mappings().all()
                
                print(f"  Toplam {len(rows)} satır veri bulundu.")
                
                if rows:
                    data_to_insert = [dict(row) for row in rows]
                    new_conn.execute(new_table.insert(), data_to_insert)
                    print(f"  {len(rows)} satır başarıyla aktarıldı.")
                    
                    # Veritabanı sequence'lerini güncelle (PostgreSQL için)
                    for col in new_table.columns:
                        if col.primary_key and col.type.python_type is int:
                            # Sequence reset query
                            seq_query = text(f"""
                                SELECT setval(
                                    pg_get_serial_sequence('{table.name}', '{col.name}'), 
                                    COALESCE((SELECT MAX({col.name}) FROM {table.name}), 1), 
                                    true
                                );
                            """)
                            try:
                                new_conn.execute(seq_query)
                                print(f"  Sequence güncellendi: {table.name}.{col.name}")
                            except Exception as e:
                                print(f"  Sequence güncellenirken bir hata oluştu: {e}")
                else:
                    print(f"  Aktarılacak veri yok.")

    print("Migrasyon %100 başarıyla tamamlandı!")

if __name__ == "__main__":
    migrate()
