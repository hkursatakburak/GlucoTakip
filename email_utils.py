import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
# If FROM_EMAIL is not set, fallback to SMTP_USERNAME
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

def send_email(to_email: str, subject: str, html_content: str):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"Warning: SMTP credentials not set. Simulated email to {to_email}: {subject}")
        print(f"Content: {html_content}")
        return

    msg = MIMEMultipart("alternative")
    msg.add_header("Subject", subject)
    msg.add_header("From", str(FROM_EMAIL))
    msg.add_header("To", to_email)

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        server = smtplib.SMTP(str(SMTP_SERVER), int(SMTP_PORT))
        server.starttls()
        server.login(str(SMTP_USERNAME), str(SMTP_PASSWORD))
        server.sendmail(str(FROM_EMAIL), to_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
