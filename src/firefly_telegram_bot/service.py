import logging
import requests
from datetime import datetime
from typing import List, Dict, Any
from .config import FIREFLY_URL, FIREFLY_TOKEN, FIREFLY_SOURCE_ID

logger = logging.getLogger(__name__)

def submit_transaction(transactions: List[Dict[str, Any]]):
    """
    Submits transactions to Firefly III API.
    Input format: [{'description': 'Coffee', 'amount': 5.00, 'date': '2023-10-10', 'store': 'Starbucks'}]
    """
    
    if not FIREFLY_URL or not FIREFLY_TOKEN:
        logger.error("Firefly credentials missing. Skipping upload.")
        return False

    url = f"{FIREFLY_URL}/api/v1/transactions"
    
    headers = {
        "Authorization": f"Bearer {FIREFLY_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Prepare the payload list based on the incoming data
    formatted_transactions = []
    
    current_date = datetime.now().strftime("%Y-%m-%d")

    for tx in transactions:
        # Construct the single transaction object
        # Corresponds to the internal object in your curl 'transactions' array
        item = {
            "type": "withdrawal",
            # Use provided date or fallback to today
            "date": tx.get("date", current_date), 
            "amount": str(tx["amount"]),
            "description": tx["description"],
            "source_id": FIREFLY_SOURCE_ID
        }
        formatted_transactions.append(item)

    payload = {
        "transactions": formatted_transactions
    }

    try:
        logger.info(f"Sending {len(formatted_transactions)} item(s) to Firefly III...")
        
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if successful (Status Code 200-299)
        if response.ok:
            logger.info("Successfully uploaded to Firefly III.")
            return True
        else:
            logger.error(f"Failed to upload. Status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error connecting to Firefly III: {e}")
        return False