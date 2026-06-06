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

# ফেক সার্ভার (রেন্ডারের জন্য)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

def run_health_check_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    httpd.serve_forever()

# ৫০০ নামের লিস্ট (সংক্ষেপে উদাহরণ, আপনি চাইলে এখানে আরও নাম যোগ করতে পারেন)
MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"] # ৫০০টি নাম যোগ করতে চাইলে এখানে আরও লিস্ট বাড়ান
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

# স্টেজস
CHOOSING_FEATURE, WAITING_2FA, GENERATING_NAME = range(3)

BOT_TOKEN = "8861233125:AAGWtKG3j1lMIU4bQXiIWbpKE4ELlxxy3qM"
OUTLOOK_WEBAPP_URL = "https://code.yamin.bd" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("Foreign Name 🌐")],
        [KeyboardButton("Password 🔑"), KeyboardButton("2FA Code 🔐")],
        [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 **FB ALL WORK Bot**-এ স্বাগতম!", reply_markup=reply_markup)
    return CHOOSING_FEATURE

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Foreign Name 🌐":
        reply_markup = ReplyKeyboardMarkup([["Male 👨", "Female 👩"], ["Back 🔙"]], resize_keyboard=True)
        await update.message.reply_text("👤 লিঙ্গ সিলেক্ট করুন:", reply_markup=reply_markup)
        return GENERATING_NAME
    elif text == "Password 🔑":
        password = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        await update.message.reply_text(f"🔐 **Password:** `{password}`", parse_mode="Markdown")
    elif text == "2FA Code 🔐":
        await update.message.reply_text("🔑 সিক্রেট কি পাঠান:")
        return WAITING_2FA
    return CHOOSING_FEATURE

async def generate_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text in ["Male 👨", "Female 👩"]:
        first_name = random.choice(MALE_NAMES) if text == "Male 👨" else random.choice(FEMALE_NAMES)
        full_name = f"{first_name} {random.choice(LAST_NAMES)}"
        await update.message.reply_text(f"✅ **Name:** `{full_name}`", parse_mode="Markdown")
    
    keyboard = [[KeyboardButton("Foreign Name 🌐")], [KeyboardButton("Password 🔑"), KeyboardButton("2FA Code 🔐")], [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]]
    await update.message.reply_text("মেনু:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return CHOOSING_FEATURE

# (2FA এবং মেইন সার্ভারের বাকি অংশ একই থাকবে)
# ... বাকি আগের কোডটি এখানে বসিয়ে দিন ...

    
