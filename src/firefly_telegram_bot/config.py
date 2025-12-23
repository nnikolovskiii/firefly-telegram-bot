import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# --- CHANGED: OpenRouter Config ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# You can use "google/gemini-2.0-flash-001" or any vision-capable model on OpenRouter
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

# Firefly III Config
FIREFLY_URL = os.getenv("FIREFLY_URL")
FIREFLY_TOKEN = os.getenv("FIREFLY_TOKEN")
FIREFLY_SOURCE_ID = os.getenv("FIREFLY_SOURCE_ID", "1")

if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Please set TELEGRAM_TOKEN and OPENROUTER_API_KEY in .env")