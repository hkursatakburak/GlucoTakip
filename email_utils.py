import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import traceback

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
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
        print("1. Connecting to SMTP Server...")
        server = smtplib.SMTP(str(SMTP_SERVER), int(SMTP_PORT))
        server.set_debuglevel(1)  # Debug logs for troubleshooting
        
        print("2. Starting TLS...")
        server.starttls()
        
        print("3. Attempting Login...")
        server.login(str(SMTP_USERNAME), str(SMTP_PASSWORD))
        
        print("4. Sending Email...")
        server.sendmail(str(FROM_EMAIL), to_email, msg.as_string())
        
        print("5. Closing Connection...")
        server.quit()
        
        print(f"✅ Success: Email securely delivered to {to_email}")
        print(f"--- EMAIL DELIVERY TRACE END ---")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        traceback.print_exc()
        print(f"--- EMAIL DELIVERY TRACE END WITH ERROR ---")
