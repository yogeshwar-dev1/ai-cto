import requests
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_all_sites() -> list:
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/sites?active=eq.true", headers=HEADERS, timeout=10)
        return res.json()
    except Exception as e:
        print(f"DB error (get_sites): {e}")
        return []

def add_site(url: str, name: str = "") -> bool:
    try:
        payload = {"url": url, "name": name or url, "active": True}
        res = requests.post(f"{SUPABASE_URL}/rest/v1/sites", json=payload, headers=HEADERS, timeout=10)
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"DB error (add_site): {e}")
        return False

def remove_site(url: str) -> bool:
    try:
        res = requests.patch(
            f"{SUPABASE_URL}/rest/v1/sites?url=eq.{url}",
            json={"active": False},
            headers=HEADERS,
            timeout=10
        )
        return res.status_code in [200, 204]
    except Exception as e:
        print(f"DB error (remove_site): {e}")
        return False

def log_uptime(site_url: str, status: str, response_time: int = None, error: str = None) -> bool:
    try:
        payload = {
            "site_url": site_url,
            "status": status,
            "response_time": response_time,
            "error": error
        }
        res = requests.post(f"{SUPABASE_URL}/rest/v1/uptime_logs", json=payload, headers=HEADERS, timeout=10)
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"DB error (log_uptime): {e}")
        return False

def log_fix(site_url: str, error: str, fix: str) -> int:
    try:
        payload = {"site_url": site_url, "error": error, "fix": fix}
        res = requests.post(f"{SUPABASE_URL}/rest/v1/fix_logs", json=payload, headers=HEADERS, timeout=10)
        data = res.json()
        if data and isinstance(data, list):
            return data[0].get("id")
        return None
    except Exception as e:
        print(f"DB error (log_fix): {e}")
        return None

def mark_fix_approved(fix_id: int, deployed: bool = False) -> bool:
    try:
        res = requests.patch(
            f"{SUPABASE_URL}/rest/v1/fix_logs?id=eq.{fix_id}",
            json={"approved": True, "deployed": deployed},
            headers=HEADERS,
            timeout=10
        )
        return res.status_code in [200, 204]
    except Exception as e:
        print(f"DB error (mark_fix): {e}")
        return False

def get_uptime_stats(site_url: str) -> dict:
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/uptime_logs?site_url=eq.{site_url}&order=checked_at.desc&limit=100",
            headers=HEADERS,
            timeout=10
        )
        logs = res.json()
        if not logs:
            return {"uptime": 100, "total": 0, "up": 0, "down": 0, "avg_response": 0}
        
        total = len(logs)
        up = sum(1 for l in logs if l["status"] == "up")
        down = total - up
        response_times = [l["response_time"] for l in logs if l["response_time"]]
        avg_response = int(sum(response_times) / len(response_times)) if response_times else 0
        
        return {
            "uptime": round((up / total) * 100, 1),
            "total": total,
            "up": up,
            "down": down,
            "avg_response": avg_response
        }
    except Exception as e:
        print(f"DB error (get_stats): {e}")
        return {"uptime": 0, "total": 0, "up": 0, "down": 0, "avg_response": 0}
