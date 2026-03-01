# 1. TEMEL İMAJ
# Resmi Python imajını kullanıyoruz. "slim" versiyonu gereksiz dosyaları içermez, daha hafiftir.
FROM python:3.13-slim

# 2. ÇALIŞMA DİZİNİ
# Konteyner içinde kodlarımızın bulunacağı klasörü belirtiyoruz.
WORKDIR /app

# 3. BAĞIMLILIKLARIN KOPYALANMASI VE YÜKLENMESİ
# Önce sadece requirements.txt dosyasını kopyalayarak Docker önbelleğini verimli kullanıyoruz.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. KODLARIN KOPYALANMASI
# Tüm proje dosyalarını (dockerignore hariç tuttukları dışında) konteynere aktarıyoruz.
COPY . .

# 5. PORT TANIMLAMASI
# Uygulamamızın 8000 portunda çalışacağını belirtiyoruz.
EXPOSE 8000

# 6. BAŞLATMA KOMUTU
# Konteyner ayağa kalktığında çalıştırılacak nihai komut (Uvicorn ile FastAPI sunucusu).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
