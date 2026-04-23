from agents.monitor_agent import check_site
from agents.fix_agent import analyze_and_fix, propose_fix
from core.telegram_bot import send_message
from core.database import get_all_sites, log_uptime, log_fix
from datetime import datetime
import smtplib
import os
import requests
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def send_push_notification(title: str, body: str, url: str = "https://ai-cto.onrender.com/dashboard.html"):
    try:
        # Get all saved push tokens from Supabase
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/push_tokens?select=token",
            headers=HEADERS, timeout=10
        )
        tokens = res.json()
        if not tokens:
            print("No push tokens found")
            return

        messages = [
            {
                "to": t["token"],
                "title": title,
                "body": body,
                "data": {"url": url},
                "sound": "default",
                "priority": "high",
                "channelId": "default"
            }
            for t in tokens
        ]

        push_res = requests.post(
            "https://exp.host/--/api/v2/push/send",
            json=messages,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"📱 Push sent: {push_res.status_code}")
    except Exception as e:
        print(f"Push notification error: {e}")

def send_email_alert(site_name, url, error, now):
    try:
        msg = MIMEText(f"""
🚨 SITE DOWN ALERT

Site: {site_name}
URL: {url}
Error: {error}
Time: {now}

Login to your dashboard:
https://ai-cto.onrender.com/dashboard.html
        """)
        msg["Subject"] = f"🚨 SITE DOWN: {site_name}"
        msg["From"] = ALERT_EMAIL
        msg["To"] = ALERT_EMAIL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(ALERT_EMAIL, ALERT_EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"📧 Email alert sent for {site_name}")
    except Exception as e:
        print(f"Email error: {e}")

def get_open_incident(site_url):
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/incidents?site_url=eq.{site_url}&status=neq.resolved&order=created_at.desc&limit=1",
            headers=HEADERS, timeout=10
        )
        data = res.json()
        return data[0] if data else None
    except Exception as e:
        print(f"Incident fetch error: {e}")
        return None

def create_incident(site_url, error):
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/incidents",
            json={
                "site_url": site_url,
                "title": f"Outage detected: {site_url}",
                "description": error,
                "status": "investigating"
            },
            headers=HEADERS, timeout=10
        )
        print(f"🚨 Incident created for {site_url}")
    except Exception as e:
        print(f"Incident create error: {e}")

def resolve_incident(incident_id):
    try:
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/incidents?id=eq.{incident_id}",
            json={"status": "resolved", "resolved_at": datetime.utcnow().isoformat()},
            headers=HEADERS, timeout=10
        )
        print(f"✅ Incident {incident_id} resolved")
    except Exception as e:
        print(f"Incident resolve error: {e}")

def main():
    sites = get_all_sites()
    if not sites:
        print("No sites in database — using env SITE_URL")
        from config.settings import SITE_URL
        sites = [{"url": SITE_URL, "name": "Main Site"}]

    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] Checking {len(sites)} site(s)...")

    for site in sites:
        url = site["url"]
        name = site.get("name", url)
        result = check_site(url)

        if result["status"] == "up":
            print(f"[{now}] ✅ {name} — {result['response_time']}ms")
            log_uptime(url, "up", result["response_time"])
            incident = get_open_incident(url)
            if incident:
                resolve_incident(incident["id"])
                send_message(f"✅ *SITE RECOVERED*\nSite: `{name}`\nTime: `{now}`")
                send_push_notification(
                    title="✅ Site Recovered",
                    body=f"{name} is back online!",
                    url=f"https://ai-cto.onrender.com/dashboard.html"
                )
        else:
            error = result.get("error", f"HTTP {result.get('code')}")
            print(f"[{now}] ❌ {name} — {error}")
            log_uptime(url, "down", error=error)
            incident = get_open_incident(url)
            if not incident:
                create_incident(url, error)
                send_message(f"🚨 *SITE DOWN*\nSite: `{name}`\nError: `{error}`\nTime: `{now}`")
                send_email_alert(name, url, error, now)
                send_push_notification(
                    title="🔴 Site Down!",
                    body=f"{name} is down — AI is analyzing...",
                    url=f"https://ai-cto.onrender.com/dashboard.html"
                )
            fix = analyze_and_fix(error)
            fix_id = log_fix(url, error, fix)
            propose_fix(error, fix)
            send_push_notification(
                title="🔧 AI Fix Proposed",
                body=f"{name}: {fix[:80]}...",
                url=f"https://ai-cto.onrender.com/dashboard.html"
            )

if __name__ == "__main__":
    main()