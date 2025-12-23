import base64
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List
from .config import OPENROUTER_API_KEY, OPENROUTER_MODEL

# Configure the client for OpenRouter
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

class ExpenseItem(BaseModel):
    description: str
    amount: float
    # AI will try to find it, otherwise it's None
    currency: str | None = None 

class ReceiptData(BaseModel):
    store_name: str
    date: str
    items: List[ExpenseItem]
    # We also check if the whole receipt has a main currency
    currency: str | None = None 

async def process_receipt_image(image_bytes: bytes) -> ReceiptData:
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    response = await client.beta.chat.completions.parse(
        model=OPENROUTER_MODEL, 
        messages=[
            {
                "role": "system", 
                # CRITICAL: Instruction to convert symbols to ISO codes
                "content": (
                    "You are an accountant. Extract data from this receipt. "
                    "Return strict JSON. "
                    "If a currency symbol is visible (like 'den', 'MKD', '€', '$'), "
                    "convert it to the 3-letter ISO code (e.g., MKD, EUR, USD). "
                    "If no currency is visible, leave it null."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this receipt image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        response_format=ReceiptData,
    )
    return response.choices[0].message.parsed