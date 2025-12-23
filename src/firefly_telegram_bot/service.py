import logging
import requests
from datetime import datetime
from typing import List, Dict, Any
from .config import (
    FIREFLY_URL, FIREFLY_TOKEN, FIREFLY_SOURCE_ID, 
    MKD_TO_EUR_RATE, USD_TO_EUR_RATE # Import new rate
)

logger = logging.getLogger(__name__)

def submit_transaction(transactions: List[Dict[str, Any]]):
    
    if not FIREFLY_URL or not FIREFLY_TOKEN:
        logger.error("Firefly credentials missing.")
        return False

    url = f"{FIREFLY_URL}/api/v1/transactions"
    headers = {
        "Authorization": f"Bearer {FIREFLY_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    formatted_transactions = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    for tx in transactions:
        currency_code = (tx.get("currency") or "MKD").upper()
        amount = float(tx["amount"])
        original_desc = ""

        # --- CONVERSION LOGIC ---
        
        # Case 1: MKD -> EUR
        if currency_code == "MKD":
            original_amount = amount
            amount = amount / MKD_TO_EUR_RATE
            currency_code = "EUR"
            logger.info(f"Converting {original_amount} MKD -> {amount:.2f} EUR")
            
        # Case 2: USD -> EUR
        elif currency_code == "USD":
            original_amount = amount
            amount = amount / USD_TO_EUR_RATE
            currency_code = "EUR"
            logger.info(f"Converting {original_amount} USD -> {amount:.2f} EUR")
            original_desc = f" (Orig: ${original_amount})"

        # Case 3: Already EUR (Do nothing)
        
        # ------------------------

        item = {
            "type": "withdrawal",
            "date": tx.get("date", current_date),
            "amount": f"{amount:.2f}",
            # Append original price to description for reference
            "description": tx["description"] + original_desc,
            "source_id": FIREFLY_SOURCE_ID,
            "destination_name": tx.get("store", "Manual Entry"),
            "currency_code": currency_code
        }
        formatted_transactions.append(item)

    payload = {"transactions": formatted_transactions}

    try:
        # ... existing request logic ...
        response = requests.post(url, json=payload, headers=headers)
        if response.ok:
            return True
        else:
            logger.error(f"Failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False