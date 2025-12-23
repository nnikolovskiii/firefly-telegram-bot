import logging
import json
import io
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from .config import TELEGRAM_TOKEN
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
        "I am your Asset Manager Bot.\n"
        "1. Send me a PHOTO of a receipt to parse it with AI.\n"
        "2. Send me JSON text to manually add an entry."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"Photo received from {user.first_name}")
    
    status_msg = await update.message.reply_text("Processing receipt with AI...")

    try:
        # Get the largest available photo
        photo_file = await update.message.photo[-1].get_file()
        
        # Download into memory
        img_byte_arr = io.BytesIO()
        await photo_file.download_to_memory(img_byte_arr)
        img_byte_arr.seek(0)
        
        # Send to AI
        receipt_data = await process_receipt_image(img_byte_arr.read())
        
        # Prepare data for service
        transactions_to_send = []
        response_text = f"**Store:** {receipt_data.store_name}\n"
        
        for item in receipt_data.items:
            response_text += f"- {item.description}: {item.amount} {item.currency}\n"
            transactions_to_send.append({
                "description": item.description,
                "amount": item.amount,
                "date": receipt_data.date,
                "store": receipt_data.store_name
            })
            
        # Send to Service
        submit_transaction(transactions_to_send)
        
        await status_msg.edit_text(f"Processed & Saved:\n{response_text}")

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await status_msg.edit_text("Failed to process receipt. Ensure it's clear.")

async def handle_manual_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Expects input in format:
    "amount": "5.00",
    "description": "Coffee"
    """
    text = update.message.text
    logger.info(f"Manual input received: {text}")
    
    try:
        # User might provide raw body, let's wrap it in curly braces if they forgot
        json_string = text.strip()
        if not json_string.startswith("{"):
            json_string = "{" + json_string + "}"
        
        data = json.loads(json_string)
        
        # Validate minimal fields
        if "amount" not in data or "description" not in data:
            await update.message.reply_text("Error: JSON must include 'amount' and 'description'.")
            return

        # Send to Service
        submit_transaction([data])
        
        await update.message.reply_text(f"Saved: {data['description']} - {data['amount']}")
        
    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON format. Please try again.")
    except Exception as e:
        logger.error(f"Error handling text: {e}")
        await update.message.reply_text("An error occurred.")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    # Handles text that isn't a command
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_manual_input))

    logger.info("Bot is running...")
    application.run_polling()