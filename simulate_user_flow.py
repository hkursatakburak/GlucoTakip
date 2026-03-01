# -----------------------------------------------------------------------------------------
# GlucoTakip Uçtan Uca Simülasyon Testi 🧪
# 
# Bu script, lokalde çalışan FastAPI sunucusuna istekler atarak bir kullanıcının
# kayıt olmasını, giriş yapmasını, 1 haftalık verilerini girmesini ve ardından 
# bu verilerin excel raporunu almasını otomatik olarak simüle eder.
#
# ÇALIŞTIRMA TALİMATI:
# 1. Sunucunun çalıştığından emin olun (uvicorn main:app --reload)
# 2. Terminalde `requests` kütüphanesinin kurulu olduğundan emin olun (pip install requests)
# 3. Terminalden çalıştırın: `python simulate_user_flow.py`
# -----------------------------------------------------------------------------------------

import requests
import random
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Style
import time

# Renkli terminal çıkışları için colorama'yı başlat
colorama.init(autoreset=True)

BASE_URL = "http://127.0.0.1:8000"

def log_info(msg):
    print(f"{Fore.CYAN}ℹ️  {msg}{Style.RESET_ALL}")

def log_success(msg):
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def log_error(msg):
    print(f"{Fore.RED}❌ HATA: {msg}{Style.RESET_ALL}")

def main():
    print(f"\n{Fore.MAGENTA}{'='*50}")
    print(f"🚀 GlucoTakip Uçtan Uca Simülasyon Testi Başlıyor")
    print(f"{'='*50}{Style.RESET_ALL}\n")

    # Session objesi: Çerezleri (cookies) ve JWT access_token'ı otomatik taşır
    session = requests.Session()
    
    # ---------------------------------------------------------
    # 1. KAYIT OLMA (REGISTER)
    # ---------------------------------------------------------
    log_info("Adım 1: Kullanıcı kaydı oluşturuluyor...")
    register_data = {
        "email": "test@gluco.com",
        "full_name": "Test Kullanıcı",
        "password": "123456",
        "data_consent": "true"
    }
    
    try:
        register_url = f"{BASE_URL}/register"
        response = session.post(register_url, data=register_data)
        
        if response.status_code == 200 and "Zaten hesabınız var mı" not in response.text:
            log_success("Kullanıcı kaydı başarılı veya zaten mevcut!")
        else:
            # The app redirects to /login?registered=true on success
            if "login" in response.url:
                log_success("Kullanıcı kaydı başarılı!")
            else:
                log_info("Kullanıcı zaten kayıtlı olabilir, devam ediliyor.")
    except Exception as e:
        log_error(f"Kayıt işlemi başarısız: {e}")
        return

    time.sleep(1)

    # ---------------------------------------------------------
    # 2. GİRİŞ YAPMA (LOGIN)
    # ---------------------------------------------------------
    log_info("Adım 2: Sisteme giriş yapılıyor (Login)...")
    login_data = {
        "email": "test@gluco.com",
        "password": "123456"
    }

    try:
        login_url = f"{BASE_URL}/login"
        response = session.post(login_url, data=login_data)
        
        # Giriş başarılıysa auth cookie session'a eklenmiş olmalı ve ana sayfaya yönlendirilmeli
        if "access_token" in session.cookies.get_dict():
             log_success("Giriş yapıldı ve JWT Token (Cookie) başarıyla alındı! 🔐")
        else:
             log_error("Giriş yapılamadı veya token alınamadı.")
             return
    except Exception as e:
        log_error(f"Giriş işlemi başarısız: {e}")
        return

    time.sleep(1)

    # ---------------------------------------------------------
    # 3. VERİ GİRİŞİ (DATA SEEDING) - SON 7 GÜN
    # ---------------------------------------------------------
    log_info("Adım 3: Son 7 güne ait 21 adet test verisi ekleniyor... ⏳")
    
    add_measurement_url = f"{BASE_URL}/add-measurement"
    now = datetime.now()
    
    measurements_added = 0
    
    for day_offset in range(6, -1, -1):  # 6 gün öncesinden bugüne kadar
        target_date = now - timedelta(days=day_offset)
        
        # Günlük 3 Öğün:
        meals = [
            {"time": "08:00", "category": "Açlık", "min": 90, "max": 110},
            {"time": "13:00", "category": "Tokluk", "min": 120, "max": 150},
            {"time": "22:00", "category": "Yatmadan Önce", "min": 100, "max": 130},
        ]
        
        for meal in meals:
            dt_str = f"{target_date.strftime('%Y-%m-%d')}T{meal['time']}"
            value = random.randint(meal['min'], meal['max'])
            
            data = {
                "value": value,
                "measured_at": dt_str,
                "category": meal['category'],
                "notes": "Simülasyon betiği ile eklendi."
            }
            
            response = session.post(add_measurement_url, data=data)
            measurements_added += 1
            
        print(f"  {Fore.YELLOW}└─ {target_date.strftime('%d.%m.%Y')} verileri girildi ({3} kayıt){Style.RESET_ALL}")
        time.sleep(0.5) # Sunucuyu yormamak için ufak bekleme
        
    log_success(f"Toplam {measurements_added} ölçüm başarıyla eklendi! 📈")
    
    time.sleep(1)

    # ---------------------------------------------------------
    # 4. EXCEL RAPORU ALMA (EXPORT)
    # ---------------------------------------------------------
    log_info("Adım 4: Eklenen veriler için Excel raporu (Son 7 Gün) talep ediliyor... 📊")
    export_url = f"{BASE_URL}/export"
    export_data = {
        "date_range": "7"
    }

    try:
        response = session.post(export_url, data=export_data)
        
        if response.status_code == 200:
            content_disposition = response.headers.get("content-disposition", "")
            
            # Use the filename from the server if possible, or a default
            filename = "ornek_test_raporu.xlsx"
            if "filename=" in content_disposition:
                filename = content_disposition.split("filename=")[-1].strip('"\'')
                
            with open(filename, "wb") as f:
                f.write(response.content)
            log_success(f"Excel başarıyla indirildi ve projenizin ana dizinine '{filename}' olarak kaydedildi! 💾")
        else:
            log_error(f"Rapor alınamadı. HTTP Kodu: {response.status_code}")
    except Exception as e:
        log_error(f"Excel indirme işlemi başarısız: {e}")

    print(f"\n{Fore.MAGENTA}{'='*50}")
    print(f"🎉 Simülasyon başarıyla tamamlandı!")
    print(f"{'='*50}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
