
import os
import requests

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_message(text: str):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ No SLACK_WEBHOOK_URL configured, skipping Slack notification")
        return

    payload = {"text": text}
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
    if resp.status_code != 200:
        print(f"Slack error: {resp.status_code} - {resp.text}")
