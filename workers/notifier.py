# notifier.py
import os
import smtplib
from email.message import EmailMessage
from xmlrpc import client
from google import genai
import requests
import json
from dotenv import load_dotenv


load_dotenv()


GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
API_KEY = os.getenv("GEM_API_KEY")

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





def send_slack_alert(drift_dict: dict):
    """
    Generates a Gemini message from drift metrics and sends it to Slack.
    Returns: the generated message text.
    """
    genai.configure(api_key=API_KEY)
    prompt = (
        "Summarize these drift metrics in 2-3 crisp sentences, highlight only anomalies:\n\n"
        + json.dumps(drift_dict, indent=2)
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    message = response.text.strip()

    slack_res = requests.post(SLACK_WEBHOOK_URL, json={"text": message})

    if slack_res.status_code != 200:
        raise Exception(f"Slack error: {slack_res.text}")