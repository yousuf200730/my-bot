import random
import string
import hmac
import hashlib
import time
import base64
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

CHOOSING_FEATURE, WAITING_2FA = range(2)

BOT_TOKEN = "8861233125:AAGWtKG3j1lMIU4bQXiIWbpKE4ELlxxy3qM"
OUTLOOK_WEBAPP_URL = "https://your-outlook-extractor-website.com" 

MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Foreign Name 🌐"), KeyboardButton("Password 🔑")],
        [KeyboardButton("2FA Code 🔐"), KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 **FB ALL WORK Bot**-এ স্বাগতম!\nমেনু থেকে সার্ভিস সিলেক্ট করুন।", reply_markup=reply_markup, parse_mode="Markdown")
    return CHOOSING_FEATURE

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Password 🔑":
        password = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        await update.message.reply_text(f"季 **Password:** `{password}`\n\n📋 _Long press to copy_", parse_mode="Markdown")
    elif text == "Foreign Name 🌐":
        full_name = f"{random.choice(random.choice([MALE_NAMES, FEMALE_NAMES]))} {random.choice(LAST_NAMES)}"
        await update.message.reply_text(f"👤 **Generated Name:**\n`{full_name}`", parse_mode="Markdown")
    elif text == "2FA Code 🔐":
        await update.message.reply_text("🔑 আপনার Facebook 2FA সিক্রেট কি-টি পাঠান:")
        return WAITING_2FA
    return CHOOSING_FEATURE

async def process_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    secret = update.message.text.strip().replace(" ", "")
    try:
        missing_padding = len(secret) % 8
        if missing_padding: secret += '=' * (8 - missing_padding)
        key = base64.b32decode(secret, casefold=True)
        intervals_no = int(time.time() // 30)
        msg = intervals_no.to_bytes(8, byteorder='big')
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        token = (int.from_bytes(h[o:o+4], byteorder='big') & 0x7fffffff) % 1000000
        await update.message.reply_text(f"🔒 **Code:**\n`{str(token).zfill(6)}`", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ সিক্রেট কি সঠিক নয়।")
    return CHOOSING_FEATURE

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_FEATURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            WAITING_2FA: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_2fa)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
  
