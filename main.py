from core.telegram_bot import send_message
from core.ai_brain import ask
from config.settings import SITE_URL, OLLAMA_MODEL
from agents.deploy_agent import full_deploy

def startup_check():
    print("Starting AI CTO...")

    # Test AI brain
    print("Testing Ollama...")
    response = ask("Reply with exactly: AI brain online")
    print(f"AI says: {response}")

    # Test Telegram
    print("Testing Telegram...")
    msg = f"""*AI CTO is online* 🤖

Watching: `{SITE_URL}`
AI Brain: `{OLLAMA_MODEL}` via Ollama
Status: All systems ready ✅

Week 1 complete. Deploy agent coming next."""

    success = send_message(msg)
    if success:
        print("Telegram message sent successfully!")
    else:
        print("Telegram failed — check your token and chat ID in .env")

if __name__ == "__main__":
    startup_check()
    full_deploy("Week 2 - Deploy Agent test")