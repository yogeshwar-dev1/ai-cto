import requests
import time
from datetime import datetime
from core.telegram_bot import send_message
from config.settings import SITE_URL

def check_site() -> dict:
    try:
        start = time.time()
        res = requests.get(SITE_URL, timeout=10)
        response_time = round((time.time() - start) * 1000)
        
        if res.status_code == 200:
            return {
                "status": "up",
                "code": res.status_code,
                "response_time": response_time
            }
        else:
            return {
                "status": "down",
                "code": res.status_code,
                "response_time": response_time
            }
    except requests.exceptions.Timeout:
        return {"status": "down", "error": "Timeout — site took too long to respond"}
    except requests.exceptions.ConnectionError:
        return {"status": "down", "error": "Connection failed — site unreachable"}
    except Exception as e:
        return {"status": "down", "error": str(e)}

def monitor_loop(interval_minutes: int = 5):
    send_message(f"👁️ *Monitor Agent started*\nChecking `{SITE_URL}` every {interval_minutes} minutes")
    
    consecutive_failures = 0
    
    while True:
        result = check_site()
        now = datetime.now().strftime("%H:%M:%S")
        
        if result["status"] == "up":
            consecutive_failures = 0
            print(f"[{now}] ✅ Site up — {result['response_time']}ms")
        else:
            consecutive_failures += 1
            error = result.get("error", f"HTTP {result.get('code')}")
            print(f"[{now}] ❌ Site down — {error}")
            
            if consecutive_failures == 1:
                send_message(f"""🚨 *SITE DOWN ALERT*
                
Site: `{SITE_URL}`
Error: `{error}`
Time: `{now}`
                
Checking again in {interval_minutes} minutes...""")
            elif consecutive_failures >= 3:
                send_message(f"""🔴 *CRITICAL: Site still down!*
                
Site: `{SITE_URL}`
Error: `{error}`
Failed checks: {consecutive_failures}
                
Please check manually!""")
        
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    monitor_loop(interval_minutes=5)