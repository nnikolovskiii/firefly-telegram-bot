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
    currency: str = "USD"

class ReceiptData(BaseModel):
    store_name: str
    date: str
    items: List[ExpenseItem]
    total_amount: float

async def process_receipt_image(image_bytes: bytes) -> ReceiptData:
    """
    Sends image bytes to OpenRouter (Gemini/GPT) to extract receipt information.
    """
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    response = await client.beta.chat.completions.parse(
        model=OPENROUTER_MODEL, 
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful accountant assistant. Extract data from this receipt. Return strict JSON."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this receipt image and return the JSON data."},
                    {
                        "type": "image_url",
                        "image_url": {
                            # OpenRouter handles this format for Gemini automatically
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        response_format=ReceiptData,
    )

    return response.choices[0].message.parsed