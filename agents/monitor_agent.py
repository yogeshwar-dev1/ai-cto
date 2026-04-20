import requests
import time
from core.telegram_bot import send_message

def check_site(url: str = None) -> dict:
    from config.settings import SITE_URL
    target = url or SITE_URL
    try:
        start = time.time()
        res = requests.get(target, timeout=10)
        response_time = round((time.time() - start) * 1000)
        if res.status_code == 200:
            return {"status": "up", "code": res.status_code, "response_time": response_time}
        else:
            return {"status": "down", "code": res.status_code, "response_time": response_time}
    except requests.exceptions.Timeout:
        return {"status": "down", "error": "Timeout — site took too long to respond"}
    except requests.exceptions.ConnectionError:
        return {"status": "down", "error": "Connection failed — site unreachable"}
    except Exception as e:
        return {"status": "down", "error": str(e)}

def monitor_loop(interval_minutes: int = 5):
    from config.settings import SITE_URL
    send_message(f"👁️ *Monitor Agent started*\nChecking every {interval_minutes} minutes")
    consecutive_failures = 0
    while True:
        result = check_site()
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        if result["status"] == "up":
            consecutive_failures = 0
            print(f"[{now}] ✅ Site up — {result['response_time']}ms")
        else:
            consecutive_failures += 1
            error = result.get("error", f"HTTP {result.get('code')}")
            print(f"[{now}] ❌ Site down — {error}")
            if consecutive_failures == 1:
                send_message(f"🚨 *SITE DOWN*\nError: `{error}`\nTime: `{now}`")
            elif consecutive_failures >= 3:
                send_message(f"🔴 *CRITICAL: Still down after {consecutive_failures} checks!*")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    monitor_loop(interval_minutes=5)
