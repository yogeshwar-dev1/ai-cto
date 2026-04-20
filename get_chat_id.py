import requests, os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
res = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
updates = res.json().get("result", [])

if updates:
    chat_id = updates[-1]["message"]["chat"]["id"]
    print(f"Your chat ID: {chat_id}")
    print("Paste this into .env as TELEGRAM_CHAT_ID")
else:
    print("No messages found - send any message to your bot first")