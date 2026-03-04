import os
import traceback
import requests

# ── Brevo API ─────────────────────────────────────────────────────────────────
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL    = os.getenv("FROM_EMAIL", "noreply@glucotakip.com")
FROM_NAME     = os.getenv("FROM_NAME", "GlucoTakip")

# ── Eski SMTP ayarları (kullanılmıyor, tanımlı bırakıldı) ─────────────────────
SMTP_SERVER   = os.getenv("SMTP_SERVER",   "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# ── Simülasyon Modu ───────────────────────────────────────────────────────────
# SIMULATE_EMAIL=true → gerçek istek atılmaz, sadece log yazılır.
SIMULATE_EMAIL = os.getenv("SIMULATE_EMAIL", "false").lower() == "true"

BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, subject: str, html_content: str):
    print("--- EMAIL DELIVERY TRACE START ---")
    print(f"To             : {to_email}")
    print(f"Subject        : {subject}")
    print(f"From           : {FROM_NAME} <{FROM_EMAIL}>")
    print(f"Provider       : Brevo HTTP API v3")
    print(f"API Key Set    : {'Yes' if BREVO_API_KEY else 'No'}")
    print(f"Simulation Mode: {'ACTIVE' if SIMULATE_EMAIL else 'OFF'}")

    # ── Simülasyon Modu ───────────────────────────────────────────────────────
    if SIMULATE_EMAIL:
        print(f"🟡 [SIMULATION MODE] Gerçek e-posta gönderilmedi. Alıcı: {to_email}")
        print(f"[SIMULATION MODE] Konu   : {subject}")
        print(f"[SIMULATION MODE] İçerik :\n{html_content}")
        print("--- EMAIL DELIVERY TRACE END (SIMULATED) ---")
        return

    if not BREVO_API_KEY:
        print("❌ BREVO_API_KEY tanımlı değil. E-posta gönderilemedi.")
        print("--- EMAIL DELIVERY TRACE END (NO API KEY) ---")
        return

    # ── Brevo API isteği ──────────────────────────────────────────────────────
    headers = {
        "accept":       "application/json",
        "content-type": "application/json",
        "api-key":      BREVO_API_KEY,
    }

    payload = {
        "sender":     {"name": FROM_NAME, "email": FROM_EMAIL},
        "to":         [{"email": to_email}],
        "subject":    subject,
        "htmlContent": html_content,
    }

    try:
        print("1. Brevo API'ye HTTP POST isteği gönderiliyor...")
        response = requests.post(BREVO_ENDPOINT, headers=headers, json=payload, timeout=15)

        print(f"2. HTTP Status : {response.status_code}")
        print(f"   Response    : {response.text}")

        if response.status_code in (200, 201):
            print(f"✅ Success: E-posta başarıyla gönderildi → {to_email}")
            print("--- EMAIL DELIVERY TRACE END ---")
        else:
            print(f"❌ Brevo API Hatası: {response.status_code} - {response.text}")
            print("--- EMAIL DELIVERY TRACE END WITH ERROR ---")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Brevo API'ye ulaşılamadı. ({type(e).__name__}: {e})")
        traceback.print_exc()
        print("--- EMAIL DELIVERY TRACE END WITH ERROR ---")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: İstek 15 saniye içinde yanıt almadı. ({type(e).__name__}: {e})")
        traceback.print_exc()
        print("--- EMAIL DELIVERY TRACE END WITH ERROR ---")
    except Exception as e:
        print(f"❌ Unexpected Error: ({type(e).__name__}: {e})")
        traceback.print_exc()
        print("--- EMAIL DELIVERY TRACE END WITH ERROR ---")


# ── HTML E-posta Şablonları ───────────────────────────────────────────────────

def _base_email_wrapper(title: str, body_html: str) -> str:
    """Tüm e-postalar için ortak marka sarmalayıcı."""
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background-color:#0f1117;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background-color:#0f1117;padding:40px 16px;">
    <tr>
      <td align="center">
        <table width="100%" style="max-width:560px;">

          <!-- Logo / Başlık -->
          <tr>
            <td align="center" style="padding-bottom:28px;">
              <div style="display:inline-block;background:linear-gradient(135deg,#3b82f6,#6366f1);
                          border-radius:16px;padding:12px 24px;">
                <span style="font-size:22px;font-weight:800;color:#ffffff;
                             letter-spacing:-0.5px;">
                  💧 GlucoTakip
                </span>
              </div>
            </td>
          </tr>

          <!-- Kart -->
          <tr>
            <td style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
                       border-radius:20px;padding:40px 36px;color:#e2e8f0;">
              {body_html}
            </td>
          </tr>

          <!-- Alt bilgi -->
          <tr>
            <td align="center" style="padding-top:24px;font-size:12px;color:#4b5563;">
              Bu e-postayı siz istemediyseniz güvenle görmezden gelebilirsiniz.<br>
              &copy; 2025 GlucoTakip &bull; Sağlıklı günler dileriz 🩺
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def build_verification_email(full_name: str, verify_url: str) -> str:
    """Kayıt sonrası gönderilen e-posta doğrulama şablonu."""
    name = full_name or "Değerli Kullanıcımız"
    body = f"""
      <h2 style="margin:0 0 8px;font-size:24px;font-weight:700;color:#ffffff;">
        Hoş geldiniz, {name}! 🎉
      </h2>
      <p style="margin:0 0 20px;font-size:15px;color:#94a3b8;line-height:1.6;">
        GlucoTakip ailesine katıldığınız için teşekkürler. Hesabınızı
        aktifleştirmek için aşağıdaki butona tıklamanız yeterli.
      </p>

      <!-- Bilgi kutusu -->
      <div style="background:rgba(59,130,246,0.1);border-left:4px solid #3b82f6;
                  border-radius:8px;padding:14px 18px;margin-bottom:28px;font-size:13px;color:#93c5fd;">
        🔒 Bu bağlantı <strong>24 saat</strong> geçerlidir.
      </div>

      <!-- Buton -->
      <div style="text-align:center;margin:28px 0;">
        <a href="{verify_url}"
           style="background:linear-gradient(135deg,#3b82f6,#6366f1);color:#ffffff;
                  text-decoration:none;padding:15px 36px;border-radius:12px;
                  font-size:16px;font-weight:700;display:inline-block;
                  letter-spacing:0.3px;">
          ✅ Hesabımı Doğrula
        </a>
      </div>

      <p style="font-size:13px;color:#6b7280;margin-top:24px;line-height:1.6;">
        Butona tıklayamıyorsanız aşağıdaki bağlantıyı tarayıcınıza yapıştırın:
      </p>
      <p style="font-size:12px;word-break:break-all;color:#3b82f6;margin:0;">
        {verify_url}
      </p>
    """
    return _base_email_wrapper("GlucoTakip — E-posta Doğrulama", body)


def build_password_reset_email(full_name: str, reset_url: str) -> str:
    """Şifre sıfırlama e-posta şablonu."""
    name = full_name or "Değerli Kullanıcımız"
    body = f"""
      <h2 style="margin:0 0 8px;font-size:24px;font-weight:700;color:#ffffff;">
        Şifre Sıfırlama Talebi 🔑
      </h2>
      <p style="margin:0 0 20px;font-size:15px;color:#94a3b8;line-height:1.6;">
        Merhaba <strong style="color:#e2e8f0;">{name}</strong>, GlucoTakip hesabınız
        için bir şifre sıfırlama talebinde bulunuldu.
      </p>

      <!-- Uyarı kutusu -->
      <div style="background:rgba(245,158,11,0.1);border-left:4px solid #f59e0b;
                  border-radius:8px;padding:14px 18px;margin-bottom:28px;font-size:13px;color:#fcd34d;">
        ⚠️ Bu bağlantı <strong>1 saat</strong> geçerlidir. Talebi siz yapmadıysanız
        bu e-postayı görmezden gelin — şifreniz değişmeyecektir.
      </div>

      <!-- Buton -->
      <div style="text-align:center;margin:28px 0;">
        <a href="{reset_url}"
           style="background:linear-gradient(135deg,#f59e0b,#ef4444);color:#ffffff;
                  text-decoration:none;padding:15px 36px;border-radius:12px;
                  font-size:16px;font-weight:700;display:inline-block;
                  letter-spacing:0.3px;">
          🔄 Şifremi Sıfırla
        </a>
      </div>

      <p style="font-size:13px;color:#6b7280;margin-top:24px;line-height:1.6;">
        Butona tıklayamıyorsanız aşağıdaki bağlantıyı tarayıcınıza yapıştırın:
      </p>
      <p style="font-size:12px;word-break:break-all;color:#f59e0b;margin:0;">
        {reset_url}
      </p>
    """
    return _base_email_wrapper("GlucoTakip — Şifre Sıfırlama", body)
