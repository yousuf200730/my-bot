import random
import string
import hmac
import hashlib
import time
import base64
import requests
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# রেন্ডারের ফেক সার্ভার
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

# ১. সিস্টেম ১: র্যান্ডম টেক্সট + আজকের তারিখ (যেমন: SGSTXV07)
def generate_date_random_password():
    random_part = "".join(random.choice(string.ascii_uppercase) for _ in range(6))
    current_day = datetime.now().strftime("%d")
    return f"{random_part}{current_day}"

# ২. সিস্টেম ২: র্যান্ডম টেক্সট + ৩টি ফিক্সড সিম্বল (যেমন: JDHSG@&@)
def generate_symbol_random_password():
    random_part = "".join(random.choice(string.ascii_uppercase) for _ in range(5)) # ৫টি অক্ষর
    symbols = "".join(random.choice("@&#$%^*!") for _ in range(3)) # শেষে ৩টি সিম্বল ফিক্সড
    return f"{random_part}{symbols}"

# ৩. সিস্টেম ৩: শুধু বড় হাতের অক্ষর (যেমন: MDKAHFG)
def generate_only_alphabet_password():
    return "".join(random.choice(string.ascii_uppercase) for _ in range(7))

# ফ্রি এআই এপিআই ফাংশন
def ask_free_ai(prompt):
    try:
        response = requests.get(f"https://api.simsimi.site/simsimi?text={prompt}&lc=bn")
        if response.status_code == 200:
            res_data = response.json()
            return res_data.get('success', 'আমি এই মুহূর্তে একটু ব্যস্ত আছি ভাই।')
        return "দুঃখিত ভাই, এআই সার্ভার সাড়া দিচ্ছে না।"
    except:
        return "কোথাও একটা সমস্যা হয়েছে, আবার চেষ্টা করুন।"

# মেইন মেনু
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Foreign Name 🌐"), KeyboardButton("AI Chatbot 🤖")],
        [KeyboardButton("Password 🔑"), KeyboardButton("2FA Code 🔐")],
        [KeyboardButton("Outlook Mail Buy 🌐", web_app=WebAppInfo(url=OUTLOOK_WEBAPP_URL))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message if update.message else update.callback_query.message
    await msg.reply_text("👋 **FB ALL WORK Bot**-এ স্বাগতম!\nমেনু থেকে সার্ভিস সিলেক্ট করুন।", reply_markup=get_main_keyboard(), parse_mode="Markdown")

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
        context.user_data['waiting_for_2fa'] = True
        context.user_data['waiting_for_ai'] = False
        await update.message.reply_text("🔑 আপনার Facebook 2FA সিক্রেট কি (Secret Key) পাঠান:")

    elif text == "AI Chatbot 🤖":
        context.user_data['waiting_for_ai'] = True
        context.user_data['waiting_for_2fa'] = False
        await update.message.reply_text("🤖 **AI মোড অ্যাক্টিভ হয়েছে!**\nএখন আপনি আমাকে যেকোনো প্রশ্ন করতে পারেন:")

# ইউজার ইনপুট প্রসেসিং
async def process_user_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if context.user_data.get('waiting_for_ai'):
        if user_text.startswith('/') or user_text in ["Foreign Name 🌐", "AI Chatbot 🤖", "Password 🔑", "2FA Code 🔐"]:
            context.user_data['waiting_for_ai'] = False
            return
            
        waiting_msg = await update.message.reply_text("🤔 ভাবছি...")
        ai_reply = ask_free_ai(user_text)
        await waiting_msg.edit_text(f"🤖 **AI:** {ai_reply}")
        
    elif context.user_data.get('waiting_for_2fa'):
        secret = user_text.strip().replace(" ", "")
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
        context.user_data['waiting_for_2fa'] = False
    else:
        await update.message.reply_text("অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করুন।", reply_markup=get_main_keyboard())

# ইনলাইন বাটন ক্লিকের লজিক (সবুজ-লাল কালার থিমসহ সম্পূর্ণ ফাংশন)
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # --- নাম জেনারেশন পার্ট ---
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
        
    # --- পাসওয়ার্ড জেনারেশন পার্ট (কালারফুল চেঞ্জিং সিস্টেম) ---
    elif data == "set_date_pass" or data == "regen_date_pass":
        password = generate_date_random_password()
        reply_text = f"🔒 **Password Generator (Date + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        keyboard = [
            [InlineKeyboardButton("✅ Date+👑", callback_data="set_date_pass"), 
             InlineKeyboardButton("❌ Symbol+👑", callback_data="set_sym_pass"), 
             InlineKeyboardButton("❌ Alphabet", callback_data="set_alpha_pass")],
            [InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_date_pass")]
        ]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "set_sym_pass" or data == "regen_sym_pass":
        password = generate_symbol_random_password()
        reply_text = f"🔒 **Password Generator (Symbol + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long speak to copy_"
        keyboard = [
            [InlineKeyboardButton("❌ Date+👑", callback_data="set_date_pass"), 
             InlineKeyboardButton("✅ Symbol+👑", callback_data="set_sym_pass"), 
             InlineKeyboardButton("❌ Alphabet", callback_data="set_alpha_pass")],
            [InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_sym_pass")]
        ]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif data == "set_alpha_pass" or data == "regen_alpha_pass":
        password = generate_only_alphabet_password()
        reply_text = f"🔒 **Password Generator (Only Alphabet)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
        keyboard = [
            [InlineKeyboardButton("❌ Date+👑", callback_data="set_date_pass"), 
             InlineKeyboardButton("❌ Symbol+👑", callback_data="set_sym_pass"), 
             InlineKeyboardButton("✅ Alphabet", callback_data="set_alpha_pass")],
            [InlineKeyboardButton("🔄 Generate New Password ✨", callback_data="regen_alpha_pass")]
        ]
        await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    threading.Thread(target=run_health_check_server, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^(Foreign Name 🌐|AI Chatbot 🤖|Password 🔑|2FA Code 🔐)$'), handle_text_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_user_inputs))
    application.add_handler(CallbackQueryHandler(handle_inline_buttons))
    
    application.run_polling()

if __name__ == '__main__':
    main()
        
