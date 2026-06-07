import random
import string
import hmac
import hashlib
import time
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# రেন্ডারের ফেক সার্ভার
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_health_check_server():
    server_address = ('', 10000)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    httpd.serve_forever()

BOT_TOKEN = "8861233125:AAGWtKG3j1lMIU4bQXiIWbpKE4ELlxxy3qM"
OUTLOOK_WEBAPP_URL = "https://code.yamin.bd" 

# ইউএসএ নামের ডাটাবেজ (এখানে ৫০০টি নাম পর্যন্ত বাড়িয়ে নিতে পারবেন)
MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]

# পাসওয়ার্ড জেনারেটর ফাংশন
def generate_random_password():
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))

# মেইন মেনু (নিচের স্থায়ী বাটনগুলো)
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Foreign Name 🌐")],
        [KeyboardButton("Password 🔑"), KeyboardButton("2FA Code 🔐")],
        [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ইউজার অবজেক্ট হ্যান্ডেল করা (মেসেজ নাকি বাটন ক্লিক)
    msg = update.message if update.message else update.callback_query.message
    await msg.reply_text("👋 **FB ALL WORK Bot**-এ স্বাগতম!\nমেনু থেকে সার্ভিস সিলেক্ট করুন।", reply_markup=get_main_keyboard(), parse_mode="Markdown")

async def handle_text_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Foreign Name 🌐":
        # ডিফল্টভাবে একটি মেল নাম জেনারেট করে ইনলাইন বাটনসহ পাঠানো
        full_name = f"{random.choice(MALE_NAMES)} {random.choice(LAST_NAMES)}"
        reply_text = f"🏷️ **Type:** Foreign • Male\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_"
        
        keyboard = [
            [InlineKeyboardButton("🌐 👨 Male", callback_data="set_male"), InlineKeyboardButton("🌐 👩 Female", callback_data="set_female")],
            [InlineKeyboardButton("✨ New Name 🔄", callback_data="regen_male")]
        ]
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif text == "Password 🔑":
        # পাসওয়ার্ড জেনারেট করে ইনলাইন বাটনসহ পাঠানো
        password = generate_random_password()
        reply_text = f"🔒 **Password Generator**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        
        keyboard = [[InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_pass")]]
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif text == "2FA Code 🔐":
        context.user_data['waiting_for_2fa'] = True
        await update.message.reply_text("🔑 আপনার Facebook 2FA সিক্রেট কি (Secret Key) পাঠান:")

async def process_2fa_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ইউজার যদি ২এফএ স্টেজে থাকে
    if context.user_data.get('waiting_for_2fa'):
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
            await update.message.reply_text(f"🔒 **2FA Code:**\n`{str(token).zfill(6)}`", parse_mode="Markdown", reply_markup=get_main_keyboard())
        except:
            await update.message.reply_text("❌ সিক্রেট কি সঠিক নয়। আবার মেইন মেনু থেকে চেষ্টা করুন।", reply_markup=get_main_keyboard())
        context.user_data['waiting_for_2fa'] = False
    else:
        # সাধারণ টেক্সট আসলে মেইন মেনু দেখানো
        await update.message.reply_text("অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করুন।", reply_markup=get_main_keyboard())

# ইনলাইন বাটন ক্লিকের লজিক (Callback Query)
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # বাটন লোডিং বন্ধ করার জন্য
    
    data = query.data
    
    if data == "set_male" or data == "regen_male":
        full_name = f"{random.choice(MALE_NAMES)} {random.choice(LAST_NAMES)}"
        reply_text = f"🏷️ **Type:** Foreign • Male\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_"
        keyboard = [
            [InlineKeyboardButton("🌐 👨 Male ✅", callback_data="set_male"), InlineKeyboardButton("🌐 👩 Female", callback_data="set_female")],
            [InlineKeyboardButton("✨ New Name 🔄", callback_data="regen_male")]
        ]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "set_female" or data == "regen_female":
        full_name = f"{random.choice(FEMALE_NAMES)} {random.choice(LAST_NAMES)}"
        reply_text = f"🏷️ **Type:** Foreign • Female\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_"
        keyboard = [
            [InlineKeyboardButton("🌐 👨 Male", callback_data="set_male"), InlineKeyboardButton("🌐 👩 Female ✅", callback_data="set_female")],
            [InlineKeyboardButton("✨ New Name 🔄", callback_data="regen_female")]
        ]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "regen_pass":
        password = generate_random_password()
        reply_text = f"🔒 **Password Generator**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        keyboard = [[InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_pass")]]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    threading.Thread(target=run_health_check_server, daemon=True).start()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # হ্যান্ডলারসমূহ
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(Foreign Name 🌐|Password 🔑|2FA Code 🔐)$'), handle_text_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_2fa_text))
    application.add_handler(CallbackQueryHandler(handle_inline_buttons))
    
    application.run_polling()

if __name__ == '__main__':
    main()
        
