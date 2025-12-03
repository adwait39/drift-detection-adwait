# notifier.py
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Correct: Load by variable *names*, not values
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

if not GMAIL_USER:
    raise RuntimeError("GMAIL_USER missing in .env")

if not GMAIL_APP_PASSWORD:
    raise RuntimeError("GMAIL_APP_PASSWORD missing in .env")


def send_email_alert(subject: str, body: str, to_email: str):
    """
    Sends an email alert using Gmail SMTP.
    """
    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL] Alert sent to {to_email}")

    except Exception as e:
        print(f"[EMAIL ERROR] Could not send Gmail alert → {e}")
