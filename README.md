# 🩸 GlucoTakip - Akıllı Şeker Asistanı

Babalarımızın ve değerli diyabet hastalarının kan şekeri ölçümlerini bir kağıda yazıp kaybetme derdine son! GlucoTakip, sağlık verilerini kolayca ve güvenle takip etmenizi sağlayan, doktor randevularında tek tıkla profesyonel bir Excel raporu sunabilen modern ve kullanıcı dostu bir zeki web uygulamasıdır. Sağlığınız parmaklarınızın ucunda, kayıt altında ve güvende! 🚀

## ✨ Öne Çıkan Özellikler

- **Işık Hızında Backend:** FastAPI altyapısıyla desteklenen, anlık veri işleyen süper hızlı mimari.
- **Tek Tıkla Güvenli Giriş (OAuth2):** Şifre ezberlemeye son! Google veya Apple hesabınızla güvenle ve hızlıca sisteme girin.
- **Modern ve Ferah Tasarım:** TailwindCSS kullanılarak geliştirilen, mobilde ve masaüstünde harika görünen cam gibi (glassmorphism) arayüz.
- **Görsel Trend Analizi:** Chart.js entegrasyonu sayesinde haftalık ve aylık şeker değişimlerinizi "İdeal Aralık" hedef bantlarıyla görsel olarak takip edin.
- **Doktor İçin Excel Raporu:** Girilen verilerinizi tek tıkla filtreleyin ve doktorunuza sunmak üzere derli toplu `.xlsx` (Excel) dosyası olarak anında indirin.
- **Simülasyon ve Data Seeding:** Yeni özellikler denerken sistemi verilerle doldurmak için tasarlanmış gerçekçi otomatik test simülasyonu betiği!

---

## 📸 Örnek Kullanım (Demo)

*Not: Bu bölüme uygulamanın çalışır halini gösteren GIF'ler eklenecektir.*

### 1. Tek Tıkla Giriş Yapma
Kullanıcıların şifre hatırlamakla uğraşmadan Google veya Apple hesaplarıyla sisteme saniyeler içinde giriş yaptığı o akıcı deneyim.
`![Google ile Giriş](docs/login.gif)`

### 2. Ölçüm Ekleme ve Grafikler
Yeni bir kan şekeri değerinin girilmesi ve ana sayfadaki grafiğin anında güncellenmesi.
`![Ölçüm Ekleme](docs/dashboard.gif)`

### 3. Doktor İçin Excel Raporu Alma
Girilen verilerin tek bir butona basılarak düzenli bir Excel tablosu olarak indirilmesi.
`![Excel İndir](docs/export.gif)`

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

1. **Gereksinimleri Yükleyin:**  
   Terminalinizde projenin ana dizinindeyken bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. **Çevre Değişkenlerini (Environment Variables) Ayarlayın:**  
   Projenin kök dizinindeki `.env.example` dosyasının adını `.env` olarak değiştirin ve içeriğini kendi credentials bilgilerinizle doldurun (örn. Google Client ID vb. _Bu adımı Google Cloud Console üzerinden kendi projelerinizde ID aldıktan sonra gerçekleştireceksiniz_).

3. **Sunucuyu Başlatın (Lokal Yöntem - Geliştirme İçin):**  
   Uvicorn ile FastAPI sunucusunu ayağa kaldırın:
   ```bash
   uvicorn main:app --reload
   ```
   Artık tarayıcınızdan `http://127.0.0.1:8000` adresine giderek uygulamayı kullanabilirsiniz!

4. **Docker ile Çalıştırma (Üretim/Deploy Yöntemi):**  
   Sisteminizde Docker ve Docker Compose kurulu ise, tüm uygulamayı tek satırla izole bir ortamda ayağa kaldırabilirsiniz:
   ```bash
   docker-compose up -d --build
   ```
   Bu komut projeyi derler ve arka planda çalıştırır. Uygulamaya yine `http://127.0.0.1:8000` üzerinden erişebilirsiniz. Konteynerleri durdurmak için `docker-compose down` kullanabilirsiniz.

5. **Otomatik Test Simülasyonunu Çalıştırma:**  
   Sistemin tüm süreçlerini (Kayıt, giriş, veri ekleme, Excel indirme) simüle etmek çok kolay. Sadece terminalden şu betiği çalıştırın:
   ```bash
   python simulate_user_flow.py
   ```

---
<p align="center">
  <br>
  <i><small>Bu proje Vibe Coding konseptiyle geliştirilmektedir.</small></i>
</p>
