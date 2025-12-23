import logging
import json
import io
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from .config import TELEGRAM_TOKEN, DEFAULT_CURRENCY
from .ai import process_receipt_image
from .service import submit_transaction

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"I am your Asset Manager Bot (Default Currency: {DEFAULT_CURRENCY}).\n"
        "1. Send a PHOTO of a receipt.\n"
        "2. Send JSON text manually (e.g., {\"amount\": 5, \"description\": \"Taxi\"})."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"Photo received from {user.first_name}")
    
    status_msg = await update.message.reply_text("Processing receipt with AI...")

    try:
        # Get and download photo
        photo_file = await update.message.photo[-1].get_file()
        img_byte_arr = io.BytesIO()
        await photo_file.download_to_memory(img_byte_arr)
        img_byte_arr.seek(0)
        
        # Send to AI
        receipt_data = await process_receipt_image(img_byte_arr.read())
        
        transactions_to_send = []
        response_text = f"**Store:** {receipt_data.store_name}\n"
        
        # Logic: Item Currency > Receipt Currency > Default Config
        global_currency = receipt_data.currency if receipt_data.currency else DEFAULT_CURRENCY

        for item in receipt_data.items:
            final_currency = item.currency if item.currency else global_currency
            
            response_text += f"- {item.description}: {item.amount} {final_currency}\n"
            
            transactions_to_send.append({
                "description": item.description,
                "amount": item.amount,
                "date": receipt_data.date,
                "store": receipt_data.store_name,
                "currency": final_currency
            })
            
        # Send to Service
        success = submit_transaction(transactions_to_send)
        
        if success:
            await status_msg.edit_text(f"Saved to Firefly:\n{response_text}")
        else:
            await status_msg.edit_text(f"Processed but FAILED to save:\n{response_text}")

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await status_msg.edit_text("Failed to process receipt. Please try again.")

async def handle_manual_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Expects input in format:
    "amount": "5.00",
    "description": "Coffee",
    "currency": "EUR" (Optional)
    """
    text = update.message.text
    logger.info(f"Manual input received: {text}")
    
    try:
        # User might provide raw body, wrap in braces if needed
        json_string = text.strip()
        if not json_string.startswith("{"):
            json_string = "{" + json_string + "}"
        
        data = json.loads(json_string)
        
        # Validate fields
        if "amount" not in data or "description" not in data:
            await update.message.reply_text("Error: JSON must include 'amount' and 'description'.")
            return

        # Handle Currency
        if "currency" not in data:
            data["currency"] = DEFAULT_CURRENCY

        # Send to Service
        success = submit_transaction([data])
        
        if success:
            await update.message.reply_text(f"Saved: {data['description']} - {data['amount']} {data['currency']}")
        else:
            await update.message.reply_text("Failed to save to Firefly III.")
        
    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON format.")
    except Exception as e:
        logger.error(f"Error handling text: {e}")
        await update.message.reply_text("An internal error occurred.")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_manual_input))

    logger.info("Bot is running...")
    application.run_polling()