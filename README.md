<div align="center">
  <img src="docs/Gliko_Takip_Logo.png" alt="GlucoTakip Logo" width="180">
  
  # 🩸 GlucoTakip - Akıllı Şeker Asistanı
  
  **Sağlığın Cebinde, Kontrol Sende!** 🚀
  
  <p>
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
    <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  </p>
</div>

![GlucoTakip Promo Afişi](docs/gluco-takip-promo.png)

Babalarımızın ve değerli diyabet hastalarının kan şekeri ölçümlerini bir kağıda yazıp kaybetme derdine son! **GlucoTakip**, sağlık verilerini kolayca ve güvenle takip etmenizi sağlayan, doktor randevularında tek tıkla profesyonel bir Excel raporu sunabilen modern ve kullanıcı dostu bir akıllı web uygulamasıdır. Sağlığınız parmaklarınızın ucunda, kayıt altında ve güvende! 🛡️

---

## ✨ Öne Çıkan Özellikler

- ⚡ **Işık Hızında Backend:** FastAPI altyapısıyla desteklenen, anlık veri işleyen süper hızlı mimari.
- 🔐 **Tek Tıkla Güvenli Giriş (OAuth2):** Şifre ezberlemeye son! Google veya Apple hesabınızla güvenle ve hızlıca sisteme girin.
- 🎨 **Modern ve Ferah Tasarım:** TailwindCSS kullanılarak geliştirilen, mobilde ve masaüstünde harika görünen cam gibi (glassmorphism) arayüz.
- 📈 **Görsel Trend Analizi:** Chart.js entegrasyonu sayesinde haftalık ve aylık şeker değişimlerinizi "İdeal Aralık" hedef bantlarıyla görsel olarak takip edin.
- 📑 **Doktor İçin Excel Raporu:** Girilen verilerinizi tek tıkla filtreleyin ve doktorunuza sunmak üzere derli toplu `.xlsx` (Excel) dosyası olarak anında indirin.
- 🤖 **Simülasyon ve Data Seeding:** Yeni özellikler denerken sistemi verilerle doldurmak için tasarlanmış gerçekçi otomatik test simülasyonu betiği!

---

## 📸 Uygulama İçi Görseller (Demo)

### 1. Güvenli ve Hızlı Giriş 🚪
Kullanıcıların şifre hatırlamakla uğraşmadan Google veya Apple hesaplarıyla sisteme saniyeler içinde giriş yaptığı o akıcı deneyim.
<div align="center">
  <img src="docs/login_page.png" alt="Giriş Ekranı" width="400">
</div>

### 2. Özet ve Veri Grafiği 📊
Geçmiş ölçümlerinizin haftalık veya aylık periyotlarda, ideal aralıklarla birlikte görselleştirilmiş hali.
<div align="center">
  <img src="docs/data_graph.png" alt="Veri Grafiği" width="800">
</div>

### 3. Yeni Ölçüm Ekleme 🩸
Saniyeler içinde yeni bir açlık/tokluk kan şekeri değeri girebileceğiniz modern form ekranı.
<div align="center">
  <img src="docs/add_data.png" alt="Veri Ekleme Ekranı" width="400">
</div>

### 4. Geçmiş Kayıtlar ve Excel Çıktısı 📥
Tüm ölçüm geçmişinize göz atın ve doktorunuz için tek tıkla Excel formatında indirin.
<div align="center">
  <img src="docs/last_data.png" alt="Son Veriler ve İndirme" width="800">
</div>

---

## 🗺️ Yol Haritası (Roadmap)

- [x] Proje İskeletinin Kurulması (FastAPI & SQLite)
- [x] Kullanıcı Kayıt & Giriş (Auth) Sistemi
- [x] Google / Apple SSO Entegrasyonu
- [x] Ölçüm Ekleme, Listeleme ve Grafik Ekranları
- [x] Excel Çıktısı Alma (Export Endpoint)
- [x] Otomatik Test Simülasyonu Yazılması
- [x] Docker ile Paketleme ve Deploy
- [ ] Kullanıcı Sözleşmesi ve Veri İzni (AI Çalışmaları İçin)

---

## 🛠️ Kurulum ve Çalıştırma

Projeyi lokal bilgisayarınızda çalıştırmak oldukça basittir:

**1. Gereksinimleri Yükleyin:** Terminalinizde projenin ana dizinindeyken bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt