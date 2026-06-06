import random
import string
import hmac
import hashlib
import time
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# রেন্ডারের পোর্ট এরর দূর করার জন্য ফেক সার্ভার
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_health_check_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print("Health check server started on port 10000...")
    httpd.serve_forever()

# ইউজার ইন্টারফেসের স্টেজসমূহ
CHOOSING_FEATURE, WAITING_2FA, GENERATING_NAME = range(3)

BOT_TOKEN = "8861233125:AAGWtKG3j1lMIU4bQXiIWbpKE4ELlxxy3qM"
OUTLOOK_WEBAPP_URL = "https://code.yamin.bd" 

# ইউএসএ নামের লিস্ট (র‍্যান্ডম স্যাম্পল - আপনি চাইলে কমা দিয়ে আরও নাম বাড়াতে পারবেন)
MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Foreign Name 🌐")],
        [KeyboardButton("Password 🔑"), KeyboardButton("2FA Code 🔐")],
        [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 **FB ALL WORK Bot**-এ স্বাগতম!\nমেনু থেকে সার্ভিস সিলেক্ট করুন।", reply_markup=reply_markup, parse_mode="Markdown")
    return CHOOSING_FEATURE

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Foreign Name 🌐":
        reply_markup = ReplyKeyboardMarkup([["Male 👨", "Female 👩"], ["Back 🔙"]], resize_keyboard=True)
        await update.message.reply_text("👤 লিঙ্গ সিলেক্ট করুন:", reply_markup=reply_markup)
        return GENERATING_NAME
    elif text == "Password 🔑":
        password = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        await update.message.reply_text(f"🔐 **Password:** `{password}`\n\n📋 _Long press to copy_", parse_mode="Markdown")
    elif text == "2FA Code 🔐":
        await update.message.reply_text("🔑 আপনার Facebook 2FA সিক্রেট কি (Secret Key) পাঠান:")
        return WAITING_2FA
    return CHOOSING_FEATURE

async def generate_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Back 🔙":
        # মেইন মেনুতে ফেরত যাওয়া
        keyboard = [[KeyboardButton("Foreign Name 🌐")], [KeyboardButton("Password 🔑"), KeyboardButton("2FA Code 🔐")], [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]]
        await update.message.reply_text("মেইন মেনু:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return CHOOSING_FEATURE
        
    if text in ["Male 👨", "Female 👩"]:
        first_name = random.choice(MALE_NAMES) if text == "Male 👨" else random.choice(FEMALE_NAMES)
        full_name = f"{first_name} {random.choice(LAST_NAMES)}"
        await update.message.reply_text(f"✅ **Generated USA Name:**\n`{full_name}`", parse_mode="Markdown")
        return GENERATING_NAME # নাম দেওয়ার পর মেল/ফিমেল অপশনেই রাখবে যাতে আবার জেনারেট করা যায়

    return GENERATING_NAME

async def process_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    secret = update.message.text.strip().replace(" ", "")
    
    # মেইন মেনুর কিবোর্ড ব্যাক করার জন্য রেডি রাখা
    main_keyboard = [[KeyboardButton("Foreign Name 🌐")], [KeyboardButton("Password 🔑"), KeyboardButton("2FA Code 🔐")], [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]]
    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    
    try:
        missing_padding = len(secret) % 8
        if missing_padding: 
            secret += '=' * (8 - missing_padding)
        key = base64.b32decode(secret, casefold=True)
        intervals_no = int(time.time() // 30)
        msg = intervals_no.to_bytes(8, byteorder='big')
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        token = (int.from_bytes(h[o:o+4], byteorder='big') & 0x7fffffff) % 1000000
        await update.message.reply_text(f"🔒 **2FA Code:**\n`{str(token).zfill(6)}`", parse_mode="Markdown", reply_markup=reply_markup)
    except:
        await update.message.reply_text("❌ সিক্রেট কি সঠিক নয়। আবার চেষ্টা করুন বা মেইন মেনুতে ফিরে যান।", reply_markup=reply_markup)
        
    return CHOOSING_FEATURE

def main():
    # রেন্ডার সার্ভার ব্যাকগ্রাউন্ড থ্রেডে চালু করা
    threading.Thread(target=run_health_check_server, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_FEATURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
            GENERATING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_name)],
            WAITING_2FA: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_2fa)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
                        
