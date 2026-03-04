import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import traceback

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# If FROM_EMAIL is not set, fallback to SMTP_USERNAME
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

def send_email(to_email: str, subject: str, html_content: str):
    print(f"--- EMAIL DELIVERY TRACE START ---")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"SMTP Username Configured: {'Yes' if SMTP_USERNAME else 'No'}")
    print(f"SMTP Password Configured: {'Yes' if SMTP_PASSWORD else 'No'}")
    
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"Warning: SMTP credentials not set. Simulated email to {to_email}")
        print(f"Content:\n{html_content}")
        print(f"--- EMAIL DELIVERY TRACE END (SIMULATED) ---")
        return

    msg = MIMEMultipart("alternative")
    msg.add_header("Subject", subject)
    msg.add_header("From", str(FROM_EMAIL))
    msg.add_header("To", to_email)

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        print(f"1. Connecting to SMTP Server via SSL (port {SMTP_PORT})...")
        # SMTP_SSL doğrudan şifreli bağlantı kurar; starttls() gerekmez
        server = smtplib.SMTP_SSL(str(SMTP_SERVER), int(SMTP_PORT))
        server.set_debuglevel(1)  # Debug logs for troubleshooting
        
        print("2. Attempting Login...")
        server.login(str(SMTP_USERNAME), str(SMTP_PASSWORD))
        
        print("3. Sending Email...")
        server.sendmail(str(FROM_EMAIL), to_email, msg.as_string())
        
        print("4. Closing Connection...")
        server.quit()
        
        print(f"✅ Success: Email securely delivered to {to_email}")
        print(f"--- EMAIL DELIVERY TRACE END ---")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: Kullanıcı adı veya şifre hatalı. ({type(e).__name__}: {e})")
        traceback.print_exc()
        print(f"--- EMAIL DELIVERY TRACE END WITH ERROR ---")
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection Error: Sunucuya bağlanılamadı ({SMTP_SERVER}:{SMTP_PORT}). ({type(e).__name__}: {e})")
        traceback.print_exc()
        print(f"--- EMAIL DELIVERY TRACE END WITH ERROR ---")
    except OSError as e:
        print(f"❌ Network/OS Error: Ağ erişimi engellenmiş olabilir veya port kapalı. ({type(e).__name__} [Errno {e.errno}]: {e.strerror})")
        traceback.print_exc()
        print(f"--- EMAIL DELIVERY TRACE END WITH ERROR ---")
    except Exception as e:
        print(f"❌ Unexpected Error sending email to {to_email}: ({type(e).__name__}: {e})")
        traceback.print_exc()
        print(f"--- EMAIL DELIVERY TRACE END WITH ERROR ---")
