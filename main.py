from core.telegram_bot import send_message, get_updates
from core.ai_brain import ask
from core.commander import handle_command
from config.settings import SITE_URL, OLLAMA_MODEL
from agents.monitor_agent import check_site
from agents.fix_agent import analyze_and_fix, propose_fix, handle_callback
import time
from datetime import datetime

def startup_check():
    print("Starting AI CTO...")
    response = ask("Reply with exactly: AI brain online")
    print(f"AI says: {response}")
    msg = f"""*AI CTO is online* 🤖

Watching: `{SITE_URL}`
AI Brain: `{OLLAMA_MODEL}` via Ollama
Status: All systems ready ✅

Type `help` to see all commands!"""
    send_message(msg)
    print("Telegram message sent!")

def main_loop():
    consecutive_failures = 0
    last_update_id = 0
    check_interval = 300
    last_check = 0

    send_message("👁️ *AI CTO fully operational!*\nSend `help` to see what I can do.")

    while True:
        # Handle Telegram messages and button clicks
        updates = get_updates(offset=last_update_id + 1)
        for update in updates:
            last_update_id = update["update_id"]

            # Handle button clicks
            if "callback_query" in update:
                callback_data = update["callback_query"]["data"]
                handle_callback(callback_data)

            # Handle text commands
            elif "message" in update and "text" in update["message"]:
                text = update["message"]["text"]
                print(f"Command received: {text}")
                handled = handle_command(text)
                if not handled:
                    send_message(f"❓ Unknown command: `{text}`\nSend `help` to see all commands.")

        # Check site every 5 minutes
        now = time.time()
        if now - last_check >= check_interval:
            last_check = now
            result = check_site()
            timestamp = datetime.now().strftime("%H:%M:%S")

            if result["status"] == "up":
                consecutive_failures = 0
                print(f"[{timestamp}] ✅ Site up — {result['response_time']}ms")
            else:
                consecutive_failures += 1
                error = result.get("error", f"HTTP {result.get('code')}")
                print(f"[{timestamp}] ❌ Site down — {error}")

                if consecutive_failures == 1:
                    fix = analyze_and_fix(error)
                    propose_fix(error, fix)
                elif consecutive_failures >= 3:
                    send_message(f"🔴 *CRITICAL: Site down for {consecutive_failures} checks!*")

        time.sleep(3)  # Check for Telegram messages every 3 seconds

if __name__ == "__main__":
    startup_check()
    main_loop()