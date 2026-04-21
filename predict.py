import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core.telegram_bot import send_message

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get_sites():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/sites?active=eq.true", headers=HEADERS, timeout=10)
    return res.json()

def get_recent_logs(site_url):
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/uptime_logs?site_url=eq.{site_url}&order=checked_at.desc&limit=20",
        headers=HEADERS, timeout=10
    )
    return res.json()

def analyze_with_ai(site_name, logs):
    if not logs:
        return None
    summary = []
    for l in logs:
        summary.append(f"{l['checked_at']}: status={l['status']}, response_time={l['response_time']}ms")
    data_text = "\n".join(summary)

    prompt = f"""You are an AI monitoring assistant. Analyze this site's recent uptime logs and predict if it's at risk of going down soon.

Site: {site_name}
Recent logs (newest first):
{data_text}

Reply in this exact format:
RISK: High/Medium/Low
REASON: one sentence explanation
ACTION: one sentence recommendation"""

    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150
        },
        timeout=15
    )
    data = res.json()
    return data["choices"][0]["message"]["content"].strip()

def run_predictions():
    sites = get_sites()
    print(f"Running AI predictions for {len(sites)} site(s)...")

    for site in sites:
        logs = get_recent_logs(site["url"])
        prediction = analyze_with_ai(site["name"], logs)
        if not prediction:
            continue

        print(f"\n{site['name']}:\n{prediction}")

        if "RISK: High" in prediction:
            send_message(f"⚠️ *AI EARLY WARNING*\n\nSite: `{site['name']}`\n\n{prediction}")

if __name__ == "__main__":
    run_predictions()