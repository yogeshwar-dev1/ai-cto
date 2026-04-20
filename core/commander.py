import os
from core.telegram_bot import send_message
from core.ai_brain import ask
from agents.deploy_agent import full_deploy
from agents.monitor_agent import check_site
from agents.builder_agent import build_feature
from config.settings import SITE_URL
from datetime import datetime

def handle_command(text: str) -> bool:
    text = text.strip().lower()

    if text in ["status", "/status"]:
        result = check_site()
        now = datetime.now().strftime("%H:%M:%S")
        if result["status"] == "up":
            send_message(f"""📊 *Site Status Report*

🟢 Status: *Online*
⚡ Response: `{result['response_time']}ms`
🌐 URL: `{SITE_URL}`
🕐 Checked: `{now}`""")
        else:
            error = result.get("error", f"HTTP {result.get('code')}")
            send_message(f"""📊 *Site Status Report*

🔴 Status: *DOWN*
❌ Error: `{error}`
🌐 URL: `{SITE_URL}`
🕐 Checked: `{now}`""")
        return True

    elif text in ["deploy", "/deploy"]:
        send_message("🚀 Starting deployment...")
        full_deploy("Manual deploy via Telegram")
        return True

    elif text in ["help", "/help", "/start"]:
        send_message("""🤖 *AI CTO Commands*

📊 `status` — check if site is up
🚀 `deploy` — deploy latest code
🏗️ `build <description>` — build a new feature
❓ `ask <question>` — ask AI anything
📋 `help` — show this menu

*Examples:*
- `build add a contact form`
- `build make navbar blue`
- `ask what is wrong with my site`""")
        return True

    elif text.startswith("build ") or text.startswith("/build "):
        description = text.replace("/build ", "").replace("build ", "")
        send_message(f"🏗️ Building: *{description}*\nThis may take a minute...")
        build_feature(description, os.path.join(os.getcwd(), "index.html"))
        full_deploy(f"Built: {description}")
        return True

    elif text.startswith("ask ") or text.startswith("/ask "):
        question = text.replace("/ask ", "").replace("ask ", "")
        send_message(f"🧠 Thinking about: *{question}*")
        answer = ask(question)
        send_message(f"💡 *Answer:*\n{answer[:1000]}")
        return True

    return False