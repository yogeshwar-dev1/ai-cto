from agents.monitor_agent import check_site
from agents.fix_agent import analyze_and_fix, propose_fix
from core.telegram_bot import send_message
from config.settings import SITE_URL
from datetime import datetime

def main():
    result = check_site()
    now = datetime.now().strftime("%H:%M:%S")
    
    if result["status"] == "up":
        print(f"[{now}] ✅ Site up — {result['response_time']}ms")
    else:
        error = result.get("error", f"HTTP {result.get('code')}")
        print(f"[{now}] ❌ Site down — {error}")
        send_message(f"🚨 *SITE DOWN*\nError: `{error}`\nTime: `{now}`")
        fix = analyze_and_fix(error)
        propose_fix(error, fix)

if __name__ == "__main__":
    main()