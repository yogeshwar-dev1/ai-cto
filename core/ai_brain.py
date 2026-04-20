import requests
from config.settings import OLLAMA_HOST, OLLAMA_MODEL

def ask(prompt: str, system: str = "") -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or "You are an expert software engineer. Be concise and precise.",
        "stream": False
    }
    try:
        res = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60)
        return res.json().get("response", "No response from AI")
    except Exception as e:
        return f"AI brain error: {e}"

def diagnose_bug(error_log: str, code: str) -> str:
    prompt = f"""Bug report:
{error_log}

Relevant code:
{code}

Give me:
1. Root cause (1 sentence)
2. Exact fix (code only)
3. Which file and line to change"""
    return ask(prompt)

def generate_code(description: str, context: str = "") -> str:
    prompt = f"""Task: {description}
{"Context: " + context if context else ""}
Write clean, working code. No explanations, just code."""
    return ask(prompt)