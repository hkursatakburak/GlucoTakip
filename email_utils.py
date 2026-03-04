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
