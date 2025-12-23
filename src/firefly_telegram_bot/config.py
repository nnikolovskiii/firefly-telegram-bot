import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# OpenRouter (AI)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

# Firefly III
FIREFLY_URL = os.getenv("FIREFLY_URL")
FIREFLY_TOKEN = os.getenv("FIREFLY_TOKEN")
FIREFLY_SOURCE_ID = os.getenv("FIREFLY_SOURCE_ID", "1")

# Currency Settings
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "MKD")

# --- NEW: Conversion Settings ---
# Standard peg is ~61.5 or 61.6 MKD for 1 EUR
MKD_TO_EUR_RATE = float(os.getenv("MKD_TO_EUR_RATE", "61.5"))

USD_TO_EUR_RATE = float(os.getenv("USD_TO_EUR_RATE", "1.09"))


# Validation
if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Please set TELEGRAM_TOKEN and OPENROUTER_API_KEY in your .env file")

if not FIREFLY_URL or not FIREFLY_TOKEN:
    print("WARNING: FIREFLY_URL or FIREFLY_TOKEN is missing. Data will be printed but not saved.")

