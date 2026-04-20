import requests
import os
from config.settings import OLLAMA_HOST, OLLAMA_MODEL

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

def ask_groq(prompt: str, system: str = "") -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system or "You are an expert software engineer. Be concise and precise."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000
    }
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Groq error: {e}"

def ask_ollama(prompt: str, system: str = "") -> str:
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
        return f"Ollama error: {e}"

def ask(prompt: str, system: str = "") -> str:
    # Try Groq first (cloud, always on), fallback to Ollama
    if GROQ_API_KEY:
        return ask_groq(prompt, system)
    return ask_ollama(prompt, system)

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