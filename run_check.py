from agents.monitor_agent import check_site
from agents.fix_agent import analyze_and_fix, propose_fix
from core.telegram_bot import send_message
from core.database import get_all_sites, log_uptime, log_fix
from datetime import datetime
import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

ALERT_EMAIL = os.getenv("ALERT_EMAIL")
ALERT_EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")

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
        else:
            error = result.get("error", f"HTTP {result.get('code')}")
            print(f"[{now}] ❌ {name} — {error}")
            log_uptime(url, "down", error=error)
            send_message(f"🚨 *SITE DOWN*\nSite: `{name}`\nError: `{error}`\nTime: `{now}`")
            send_email_alert(name, url, error, now)
            fix = analyze_and_fix(error)
            fix_id = log_fix(url, error, fix)
            propose_fix(error, fix)

if __name__ == "__main__":
    main()