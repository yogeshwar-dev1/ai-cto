import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from core.telegram_bot import send_message

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get_sites():
    res = requests.get(f"{SUPABASE_URL}/rest/v1/sites?active=eq.true", headers=HEADERS, timeout=10)
    return res.json()

def get_weekly_stats(site_url):
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/uptime_logs?site_url=eq.{site_url}&checked_at=gte.{week_ago}&order=checked_at.desc",
        headers=HEADERS, timeout=10
    )
    logs = res.json()
    if not logs:
        return {"uptime": 0, "total": 0, "avg_response": 0, "outages": 0}
    total = len(logs)
    up = sum(1 for l in logs if l["status"] == "up")
    outages = sum(1 for l in logs if l["status"] == "down")
    times = [l["response_time"] for l in logs if l["response_time"]]
    avg = int(sum(times) / len(times)) if times else 0
    return {
        "uptime": round((up / total) * 100, 1),
        "total": total,
        "avg_response": avg,
        "outages": outages
    }

def get_weekly_incidents():
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/incidents?created_at=gte.{week_ago}&order=created_at.desc",
        headers=HEADERS, timeout=10
    )
    return res.json()

def send_weekly_report():
    sites = get_sites()
    incidents = get_weekly_incidents()
    now = datetime.now().strftime("%B %d, %Y")

    msg = f"📊 *Weekly Report — {now}*\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🌐 *Sites Monitored:* {len(sites)}\n"
    msg += f"🚨 *Incidents This Week:* {len(incidents)}\n\n"
    msg += f"📈 *Site Performance:*\n\n"

    slowest_site = None
    slowest_time = 0

    for site in sites:
        stats = get_weekly_stats(site["url"])
        uptime_emoji = "🟢" if stats["uptime"] >= 99 else "🟡" if stats["uptime"] >= 95 else "🔴"
        msg += f"{uptime_emoji} *{site['name']}*\n"
        msg += f"   📈 Uptime: {stats['uptime']}%\n"
        msg += f"   ⚡ Avg Response: {stats['avg_response']}ms\n"
        msg += f"   ❌ Outages: {stats['outages']}\n"
        msg += f"   🔍 Total Checks: {stats['total']}\n\n"

        if stats["avg_response"] > slowest_time:
            slowest_time = stats["avg_response"]
            slowest_site = site["name"]

    if slowest_site:
        msg += f"🐢 *Slowest Site:* {slowest_site} ({slowest_time}ms avg)\n\n"

    if incidents:
        msg += f"🚨 *Recent Incidents:*\n"
        for i in incidents[:3]:
            status = "✅ Resolved" if i["status"] == "resolved" else "⚠️ Ongoing"
            msg += f"• {i['title']} — {status}\n"
    else:
        msg += f"✅ *No incidents this week!*\n"

    msg += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"🤖 AI CTO Weekly Report"

    send_message(msg)
    print("✅ Weekly report sent!")

if __name__ == "__main__":
    send_weekly_report()