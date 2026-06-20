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

MALE_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark"]
FEMALE_NAMES = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]

# ইউজারের স্টেট সেভ রাখার জন্য
USER_STATES = {}

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def edit_message(chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "Foreign Name 🌐"}, {"text": "Password 🔑"}],
            [{"text": "2FA Code 🔐"}, {"text": "Get Hotmail Code ✉️"}],
            [{"text": "Outlook Mail Buy 🌐", "web_app": {"url": OUTLOOK_WEBAPP_URL}}]
        ],
        "resize_keyboard": True
    }

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
                otp_list.append(f"{index}. `{match.group(0)}`")
                
        if otp_list:
            return "✅ **OTP FOUND:**\n\n" + "\n".join(otp_list)
        else:
            return "❌ ইনবক্স রিড করা হয়েছে, কিন্তু কোনো ৬ ডিজিটের কোড পাওয়া যায়নি।"
    except Exception as e:
        return f"❌ কানেকশন এরর: {str(e)}"

def handle_update(update):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            USER_STATES[chat_id] = None
            send_message(chat_id, "👋 **FB ALL WORK Bot**-এ স্বাগতম!\nমেনু থেকে SERVICE সিলেক্ট করুন।", get_main_keyboard())
            
        elif text == "Foreign Name 🌐":
            full_name = f"{random.choice(MALE_NAMES)} {random.choice(LAST_NAMES)}"
            reply_text = f"🏷️ **Type:** Foreign • Male\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_"
            markup = {
                "inline_keyboard": [
                    [{"text": "🌐 👨 Male ✅", "callback_data": "set_male"}, {"text": "🌐 👩 Female", "callback_data": "set_female"}],
                    [{"text": "✨ New Name 🔄", "callback_data": "regen_male"}]
                ]
            }
            send_message(chat_id, reply_text, markup)
            
        elif text == "Password 🔑":
            password = f"{''.join(random.choice(string.ascii_uppercase) for _ in range(6))}{datetime.now().strftime('%d')}"
            reply_text = f"🔒 **Password Generator (Date + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_"
            markup = {
                "inline_keyboard": [
                    [{"text": "✅ Date+👑", "callback_data": "set_date_pass"}, {"text": "❌ Symbol+👑", "callback_data": "set_sym_pass"}, {"text": "❌ Alphabet", "callback_data": "set_alpha_pass"}],
                    [{"text": "🔄 Generate New Password ✨", "callback_data": "regen_date_pass"}]
                ]
            }
            send_message(chat_id, reply_text, markup)
            
        elif text == "2FA Code 🔐":
            USER_STATES[chat_id] = "waiting_2fa"
            send_message(chat_id, "🔑 আপনার Facebook 2FA সিক্রেট কি (Secret Key) পাঠান:")
            
        elif text == "Get Hotmail Code ✉️":
            USER_STATES[chat_id] = "waiting_hotmail"
            send_message(chat_id, "📧 **Mail Data দিন:**\n\n`Format: email|pass|refresh_token|client_id`")
            
        else:
            state = USER_STATES.get(chat_id)
            if state == "waiting_2fa":
                secret = text.replace(" ", "")
                try:
                    missing_padding = len(secret) % 8
                    if missing_padding: secret += '=' * (8 - missing_padding)
                    key = base64.b32decode(secret, casefold=True)
                    intervals_no = int(time.time() // 30)
                    msg = intervals_no.to_bytes(8, byteorder='big')
                    h = hmac.new(key, msg, hashlib.sha1).digest()
                    o = h[19] & 15
                    token = (int.from_bytes(h[o:o+4], byteorder='big') & 0x7fffffff) % 1000000
                    send_message(chat_id, f"🔒 **2FA Code:**\n`{str(token).zfill(6)}`", get_main_keyboard())
                except:
                    send_message(chat_id, "❌ সিক্রেট কি সঠিক নয়। আবার চেষ্টা করুন।", get_main_keyboard())
                USER_STATES[chat_id] = None
                
            elif state == "waiting_hotmail":
                parts = text.split('|')
                if len(parts) >= 4:
                    refresh_token = parts[2].strip()
                    client_id = parts[3].strip()
                    
                    # টেম্পোরারি মেসেজ পাঠানো ও এপিআই কল
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    res = requests.post(url, json={"chat_id": chat_id, "text": "⏳ ওটিপি (OTP) খোঁজা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন..."}).json()
                    msg_id = res.get("result", {}).get("message_id")
                    
                    result = extract_hotmail_otp(refresh_token, client_id)
                    if msg_id:
                        edit_message(chat_id, msg_id, result)
                    else:
                        send_message(chat_id, result)
                else:
                    send_message(chat_id, "❌ ভুল ফরম্যাট! অনুগ্রহ করে সঠিক ফরম্যাটে ডাটা দিন:\n`email|pass|refresh_token|client_id`")
                USER_STATES[chat_id] = None
            else:
                send_message(chat_id, "অনুগ্রহ করে নিচের মেনু বাটন ব্যবহার করুন।", get_main_keyboard())

    elif "callback_query" in update:
        callback = update["callback_query"]
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        data = callback["data"]
        
        # কলব্যাক কুয়েরি অ্যান্সার করা
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": callback["id"]})
        
        if data in ["set_male", "regen_male"]:
            full_name = f"{random.choice(MALE_NAMES)} {random.choice(LAST_NAMES)}"
            markup = {"inline_keyboard": [[{"text": "🌐 👨 Male ✅", "callback_data": "set_male"}, {"text": "🌐 👩 Female", "callback_data": "set_female"}], [{"text": "✨ New Name 🔄", "callback_data": "regen_male"}]]}
            edit_message(chat_id, message_id, f"🏷️ **Type:** Foreign • Male\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_", markup)
        elif data in ["set_female", "regen_female"]:
            full_name = f"{random.choice(FEMALE_NAMES)} {random.choice(LAST_NAMES)}"
            markup = {"inline_keyboard": [[{"text": "🌐 👨 Male", "callback_data": "set_male"}, {"text": "🌐 👩 Female ✅", "callback_data": "set_female"}], [{"text": "✨ New Name 🔄", "callback_data": "regen_female"}]]}
            edit_message(chat_id, message_id, f"🏷️ **Type:** Foreign • Female\n\n👤 **Name:** `{full_name}`\n\n📋 _Long press to copy_", markup)
        elif data in ["set_date_pass", "regen_date_pass"]:
            password = f"{''.join(random.choice(string.ascii_uppercase) for _ in range(6))}{datetime.now().strftime('%d')}"
            markup = {"inline_keyboard": [[{"text": "✅ Date+👑", "callback_data": "set_date_pass"}, {"text": "❌ Symbol+👑", "callback_data": "set_sym_pass"}, {"text": "❌ Alphabet", "callback_data": "set_alpha_pass"}], [{"text": "🔄 Generate New Password ✨", "callback_data": "regen_date_pass"}]]}
            edit_message(chat_id, message_id, f"🔒 **Password Generator (Date + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_", markup)
        elif data in ["set_sym_pass", "regen_sym_pass"]:
            password = f"{''.join(random.choice(string.ascii_uppercase) for _ in range(5))}{''.join(random.choice('@&*$!') for _ in range(3))}"
            markup = {"inline_keyboard": [[{"text": "❌ Date+👑", "callback_data": "set_date_pass"}, {"text": "✅ Symbol+👑", "callback_data": "set_sym_pass"}, {"text": "❌ Alphabet", "callback_data": "set_alpha_pass"}], [{"text": "🔄 Generate New Password ✨", "callback_data": "regen_sym_pass"}]]}
            edit_message(chat_id, message_id, f"🔒 **Password Generator (Symbol + Random)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_", markup)
        elif data in ["set_alpha_pass", "regen_alpha_pass"]:
            password = "".join(random.choice(string.ascii_uppercase) for _ in range(7))
            markup = {"inline_keyboard": [[{"text": "❌ Date+👑", "callback_data": "set_date_pass"}, {"text": "❌ Symbol+👑", "callback_data": "set_sym_pass"}, {"text": "✅ Alphabet", "callback_data": "set_alpha_pass"}], [{"text": "🔄 Generate New Password ✨", "callback_data": "regen_alpha_pass"}]]}
            edit_message(chat_id, message_id, f"🔒 **Password Generator (Only Alphabet)**\n\n🧾 **Password:** `{password}`\n\n📋 _Long press to copy_", markup)

def poll_updates():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20"
            response = requests.get(url, timeout=25).json()
            if response.get("ok") and response.get("result"):
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    handle_update(update)
        except:
            time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=run_health_check_server, daemon=True).start()
    poll_updates()
