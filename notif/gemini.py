
import requests
import json

API_KEY = "AIzaSyD4gXJ4UaNhiyH62NUH9htVceCA4m9Dg3g"
from google import genai
import json

client = genai.Client(api_key="AIzaSyD4gXJ4UaNhiyH62NUH9htVceCA4m9Dg3g")

def gemini_generate_message(drift_dict: dict) -> str:
    """
    Simple: takes drift metrics dict → returns a short Gemini summary.
    """
    prompt = (
        "Summarize these drift metrics in 2-3 crisp sentences, highlight any anomalies:\n\n"
        + json.dumps(drift_dict, indent=2)
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


msg = gemini_generate_message({"semantic_mean": 0.76, "topic_kl": 1.22, "ood_rate": 0.05})
print(msg)
