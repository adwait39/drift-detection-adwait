# notifier.py
import os
import smtplib
from email.message import EmailMessage
import json
import requests
from google.generativeai import client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Correct: Load by variable *names*, not values
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GEMINI_API_KEY = os.getenv("Gemini_API_KEY")


def send_drift_alert(drift_dict: dict, subject: str, body: str, to_email: str) -> str:
    """
    Generates a Gemini message from drift metrics and sends it to Slack.
    Returns: the generated message text.
    """

    # 1) Prepare prompt for Gemini
    prompt = (
        "Summarize these drift metrics in 2-3 crisp sentences, highlight only anomalies:\n\n"
        + json.dumps(drift_dict, indent=2)
    )

    # 2) Call Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    message = response.text.strip()

    # Send email alert
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

    # 3) Send to Slack
    slack_res = requests.post(SLACK_WEBHOOK_URL, json={"text": message})

    if slack_res.status_code != 200:
        raise Exception(f"Slack error: {slack_res.text}")

    return message

