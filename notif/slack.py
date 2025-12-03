from google import genai
import requests
import json

# --- Gemini API Key ---
client = genai.Client(api_key="AIzaSyD4gXJ4UaNhiyH62NUH9htVceCA4m9Dg3g")

# --- Your Slack Webhook URL ---
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"


def send_drift_alert(drift_dict: dict) -> str:
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

    # 3) Send to Slack
    slack_res = requests.post(SLACK_WEBHOOK_URL, json={"text": message})

    if slack_res.status_code != 200:
        raise Exception(f"Slack error: {slack_res.text}")

    return message


# ------------------------
# Example usage
# ------------------------
if __name__ == "__main__":
    metrics = {
        "semantic_mean": 0.76,
        "topic_kl": 1.22,
        "ood_rate": 0.05
    }

    msg = send_drift_alert(metrics)
    print("Sent to Slack:", msg)
