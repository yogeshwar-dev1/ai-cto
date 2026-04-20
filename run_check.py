from agents.monitor_agent import check_site
from agents.fix_agent import analyze_and_fix, propose_fix
from core.telegram_bot import send_message
from core.database import get_all_sites, log_uptime, log_fix
from datetime import datetime

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
            fix = analyze_and_fix(error)
            fix_id = log_fix(url, error, fix)
            propose_fix(error, fix, fix_id=fix_id)

if __name__ == "__main__":
    main()
