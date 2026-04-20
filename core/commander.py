import os
from core.telegram_bot import send_message
from core.ai_brain import ask
from agents.deploy_agent import full_deploy
from agents.monitor_agent import check_site
from agents.builder_agent import build_feature
from core.database import get_all_sites, add_site, remove_site, get_uptime_stats
from config.settings import SITE_URL
from datetime import datetime

def handle_command(text: str) -> bool:
    cmd = text.strip().lower()

    if cmd in ["status", "/status"]:
        sites = get_all_sites()
        if not sites:
            sites = [{"url": SITE_URL, "name": "Main Site"}]
        msg = "📊 *Status Report*\n\n"
        for site in sites:
            result = check_site(site["url"])
            stats = get_uptime_stats(site["url"])
            now = datetime.now().strftime("%H:%M:%S")
            if result["status"] == "up":
                msg += f"🟢 *{site['name']}*\n⚡ {result['response_time']}ms | 📈 {stats['uptime']}% uptime\n🌐 `{site['url']}`\n\n"
            else:
                error = result.get("error", f"HTTP {result.get('code')}")
                msg += f"🔴 *{site['name']}*\n❌ `{error}`\n🌐 `{site['url']}`\n\n"
        send_message(msg.strip())
        return True

    elif cmd in ["deploy", "/deploy"]:
        send_message("🚀 Starting deployment...")
        full_deploy("Manual deploy via Telegram")
        return True

    elif cmd in ["listsites", "/listsites", "sites"]:
        sites = get_all_sites()
        if not sites:
            send_message("No sites in database yet. Use `addsite <url>` to add one!")
        else:
            msg = "🌐 *Monitored Sites*\n\n"
            for i, site in enumerate(sites, 1):
                stats = get_uptime_stats(site["url"])
                msg += f"{i}. *{site['name']}*\n   `{site['url']}`\n   📈 {stats['uptime']}% uptime ({stats['total']} checks)\n\n"
            send_message(msg.strip())
        return True

    elif cmd.startswith("addsite ") or cmd.startswith("/addsite "):
        url = cmd.replace("/addsite ", "").replace("addsite ", "").strip()
        if not url.startswith("http"):
            url = "https://" + url
        send_message(f"➕ Adding site: `{url}`...")
        result = check_site(url)
        if add_site(url, url):
            status = f"✅ Up ({result['response_time']}ms)" if result["status"] == "up" else f"❌ Down"
            send_message(f"✅ Site added!\n🌐 `{url}`\nCurrent status: {status}")
        else:
            send_message(f"❌ Failed to add site (might already exist)")
        return True

    elif cmd.startswith("removesite ") or cmd.startswith("/removesite "):
        url = cmd.replace("/removesite ", "").replace("removesite ", "").strip()
        if remove_site(url):
            send_message(f"🗑️ Site removed: `{url}`")
        else:
            send_message(f"❌ Could not remove site")
        return True

    elif cmd in ["help", "/help", "/start"]:
        send_message("""🤖 *AI CTO Commands*

📊 `status` — check all sites
🌐 `listsites` — show all monitored sites
➕ `addsite <url>` — add a new site to monitor
🗑️ `removesite <url>` — remove a site
🚀 `deploy` — deploy latest code
🏗️ `build <description>` — build a feature
❓ `ask <question>` — ask AI anything
📋 `help` — show this menu

*Examples:*
- `addsite https://mysite.com`
- `build add a contact form`
- `ask why is my site slow`""")
        return True

    elif cmd.startswith("build ") or cmd.startswith("/build "):
        description = cmd.replace("/build ", "").replace("build ", "")
        send_message(f"🏗️ Building: *{description}*\nThis may take a minute...")
        build_feature(description, os.path.join(os.getcwd(), "index.html"))
        full_deploy(f"Built: {description}")
        return True

    elif cmd.startswith("ask ") or cmd.startswith("/ask "):
        question = cmd.replace("/ask ", "").replace("ask ", "")
        send_message(f"🧠 Thinking about: *{question}*")
        answer = ask(question)
        send_message(f"💡 *Answer:*\n{answer[:1000]}")
        return True

    return False
