import random
import string
import hmac
import hashlib
import time
import base64
import requests
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# রেন্ডারের হেলথ চেক সার্ভার
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

# ইউএসএ নামের ডাটাবেজ
MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]

def generate_date_random_password():
    random_part = "".join(random.choice(string.ascii_uppercase) for _ in range(6))
    current_day = datetime.now().strftime("%d")
    return f"{random_part}{current_day}"

def generate_symbol_random_password():
    random_part = "".join(random.choice(string.ascii_uppercase) for _ in range(5))
    symbols = "".join(random.choice("@&*$!") for _ in range(3))
    return f"{random_part}{symbols}"

def generate_only_alphabet_password():
    return "".join(random.choice(string.ascii_uppercase) for _ in range(7))

# হটমেইল ওটিপি এক্সট্রাক্টর মেথড
def extract_hotmail_otp(refresh_token, client_id):
    try:
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": "https://graph.microsoft.com/mail.read"
        }
        res = requests.post(url, data=data, timeout=10).json()
        access_token = res.get("access_token")
        
        if not access_token:
            return "❌ এক্সেস টোকেন পাওয়া যায়নি! আপনার সাবমিট করা ডাটা চেক করুন বা রিফ্রেস টোকেন ডেড।"
            
        mail_url = "https://graph.microsoft.com/v1.0/me/messages?$top=5"
        headers = {"Authorization": f"Bearer {access_token}"}
        mail_res = requests.get(mail_url, headers=headers, timeout=10).json()
        
        messages = mail_res.get("value", [])
        if not messages:
            return "❌ ইনবক্সে কোনো নতুন ওটিপি বা মেসেজ পাওয়া যায়নি!"
            
        otp_list = []
        for index, msg in enumerate(messages, 1):
            body = msg.get("body", {}).get("content", "")
            subject = msg.get("subject", "")
            
            match = re.search(r'\b\d{6}\b', subject + body)
            if match:
                otp_list.append(f"{index}. {match.group(0)}")
                
        if otp_list:
            return "✅ **OTP FOUND:**\n\n" + "\n".join(otp_list)
        else:
            return "❌ ইনবক্স রিড করা হয়েছে, কিন্তু কোনো ৬ ডিজিটের কোড পাওয়া যায়নি।"
            
    except Exception as e:
        return f"❌ কানেকশন এরর: {str(e)}"

# কিবোর্ড লেআউট
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Foreign Name 🌐"), KeyboardButton("Password 🔑")],
        [KeyboardButton("2FA Code 🔐"), KeyboardButton("Get Hotmail Code ✉️")],
        [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message if update.message else update.callback_query.message
    await msg.reply_text("👋 **FB ALL WORK Bot**-এ স্বাগতম!\nমেনু থেকে SERVICE সিলেক্ট করুন।", reply_markup=get_main_keyboard(), parse_mode="Markdown")

async def handle_text_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Foreign Name 🌐":
        full_name = f"{random.choice(MALE_NAMES)} {random.choice(LAST_NAMES)}"
        reply_text = f"🏷️ **Type:** Foreign • Male\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_"
        keyboard = [
            [InlineKeyboardButton("🌐 👨 Male", callback_data="set_male"), InlineKeyboardButton("🌐 👩 Female", callback_data="set_female")],
            [InlineKeyboardButton("✨ New Name 🔄", callback_data="regen_male")]
        ]
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif text == "Password 🔑":
        password = generate_date_random_password()
        reply_text = f"🔒 **Password Generator (Date + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        keyboard = [
            [InlineKeyboardButton("✅ Date+👑", callback_data="set_date_pass"), 
             InlineKeyboardButton("❌ Symbol+👑", callback_data="set_sym_pass"), 
             InlineKeyboardButton("❌ Alphabet", callback_data="set_alpha_pass")],
            [InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_date_pass")]
        ]
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif text == "2FA Code 🔐":
        context.user_data['waiting_for_input'] = '2fa'
        await update.message.reply_text("🔑 আপনার Facebook 2FA সিক্রেট কি (Secret Key) পাঠান:")
        
    elif text == "Get Hotmail Code ✉️":
        context.user_data['waiting_for_input'] = 'hotmail'
        await update.message.reply_text("📧 **Mail Data দিন:**\n\n`Format: email|pass|refresh_token|client_id`", parse_mode="Markdown")

async def process_user_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    state = context.user_data.get('waiting_for_input')
    
    if state == '2fa':
        secret = user_text.replace(" ", "")
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
            await update.message.reply_text("❌ সিক্রেট কি সঠিক নয়। আবার চেষ্টা করুন।", reply_markup=get_main_keyboard())
        context.user_data['waiting_for_input'] = None
        
    elif state == 'hotmail':
        parts = user_text.split('|')
        if len(parts) >= 4:
            refresh_token = parts[2].strip()
            client_id = parts[3].strip()
            
            status_msg = await update.message.reply_text("⏳ ওটিপি (OTP) খোঁজা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")
            result = extract_hotmail_otp(refresh_token, client_id)
            await status_msg.edit_text(result, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ ভুল ফরম্যাট! অনুগ্রহ করে স্ক্রিনের ফরম্যাট অনুযায়ী ডাটা দিন:\n`email|pass|refresh_token|client_id`", parse_mode="Markdown")
        context.user_data['waiting_for_input'] = None
    else:
        await update.message.reply_text("অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করুন।", reply_markup=get_main_keyboard())

async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer(); data = query.data
    if data == "set_male" or data == "regen_male":
        full_name = f"{random.choice(MALE_NAMES)} {random.choice(LAST_NAMES)}"
        reply_text = f"🏷️ **Type:** Foreign • Male\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_"
        keyboard = [[InlineKeyboardButton("🌐 👨 Male ✅", callback_data="set_male"), InlineKeyboardButton("🌐 👩 Female", callback_data="set_female")], [InlineKeyboardButton("✨ New Name 🔄", callback_data="regen_male")]]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "set_female" or data == "regen_female":
        full_name = f"{random.choice(FEMALE_NAMES)} {random.choice(LAST_NAMES)}"
        reply_text = f"🏷️ **Type:** Foreign • Female\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_"
        keyboard = [[InlineKeyboardButton("🌐 👨 Male", callback_data="set_male"), InlineKeyboardButton("🌐 👩 Female ✅", callback_data="set_female")], [InlineKeyboardButton("✨ New Name 🔄", callback_data="regen_female")]]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "set_date_pass" or data == "regen_date_pass":
        password = generate_date_random_password()
        reply_text = f"🔒 **Password Generator (Date + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        keyboard = [[InlineKeyboardButton("✅ Date+👑", callback_data="set_date_pass"), InlineKeyboardButton("❌ Symbol+👑", callback_data="set_sym_pass"), InlineKeyboardButton("❌ Alphabet", callback_data="set_alpha_pass")], [InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_date_pass")]]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "set_sym_pass" or data == "regen_sym_pass":
        password = generate_symbol_random_password()
        reply_text = f"🔒 **Password Generator (Symbol + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        keyboard = [[InlineKeyboardButton("❌ Date+👑", callback_data="set_date_pass"), InlineKeyboardButton("✅ Symbol+👑", callback_data="set_sym_pass"), InlineKeyboardButton("❌ Alphabet", callback_data="set_alpha_pass")], [InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_sym_pass")]]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "set_alpha_pass" or data == "regen_alpha_pass":
        password = generate_only_alphabet_password()
        reply_text = f"🔒 **Password Generator (Only Alphabet)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        keyboard = [[InlineKeyboardButton("❌ Date+👑", callback_data="set_date_pass"), InlineKeyboardButton("❌ Symbol+👑", callback_data="set_sym_pass"), InlineKeyboardButton("✅ Alphabet", callback_data="set_alpha_pass")], [InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_alpha_pass")]]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    threading.Thread(target=run_health_check_server, daemon=True).start()
    
    # এরর এড়াতে বিল্ড মেকানিজম ফিক্স করা হয়েছে
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(Foreign Name 🌐|Password 🔑|2FA Code 🔐|Get Hotmail Code ✉️)$'), handle_text_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_user_inputs))
    application.add_handler(CallbackQueryHandler(handle_inline_buttons))
    
    # স্টার্ট পোলিং মেথড
    application.run_polling(close_loop=False)

if __name__ == '__main__':
    main()
    
