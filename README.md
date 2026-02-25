# 🩸 GlucoTakip - Akıllı Şeker Asistanı 🩺

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwind_css-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

🤖 **Modern Web teknolojileriyle (FastAPI & Tailwind) geliştirilen, diyabet hastalarının (özellikle babalarımızın 🧔) günlük şeker takibini kolaylaştıran dijital asistan.**

Karmaşık sağlık uygulamalarından sıkılanlar için çok temiz, sade ve **mobil öncelikli** tasarlandı. Büyük butonlar, okunabilir metinler ve anlaşılır grafikler içerir. 📱💙

---

## 🗺️ Yol Haritası (Roadmap)

- [x] 🏗️ Proje İskeletinin Kurulması ve Dosya Yapısı (Tamamlandı)
- [ ] 💾 Veritabanı Modelleri ve Bağlantısı
- [ ] 🔐 Kullanıcı Kayıt & Giriş (Auth) Sistemi
- [ ] 📝 Ölçüm Ekleme ve Listeleme Ekranları
- [ ] 📈 Grafiksel Raporlama (Chart.js)
- [ ] 📑 Excel Çıktısı Alma (Doktor Sunumu İçin)
- [ ] 🐳 Docker ile Paketleme ve Deploy

---

## 🚀 Kurulum ve Çalıştırma

Projeyi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

### 1. Dosyaları Kopyalayın ve Dizine Gidin
```bash
git clone <sizin-repo-linkiniz>
cd GlucoTakip
```

### 2. Sanal Ortam (Virtual Environment) Oluşturun
```bash
python -m venv venv
```
* **Windows için aktifleştirme:** `.\venv\Scripts\activate`
* **Mac/Linux için aktifleştirme:** `source venv/bin/activate`

### 3. Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Uygulamayı Başlatın
```bash
uvicorn main:app --reload
```
Tarayıcınızda [http://127.0.0.1:8000](http://127.0.0.1:8000) adresine giderek asistanınızı kullanmaya başlayabilirsiniz! 🎉

---

<br><br>
<sub>*Bu proje Vibe Coding konseptiyle, Antigravity ve Gemini desteğiyle geliştirilmektedir.*</sub>
