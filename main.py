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

# আপনার আগের সব ফাংশন এবং এআই সিস্টেম ঠিকই থাকছে, শুধু পাসওয়ার্ড ও কালার বাটনগুলো আপডেট করছি
def generate_symbol_random_password():
    random_part = "".join(random.choice(string.ascii_uppercase) for _ in range(5)) # ৫টি অক্ষর
    symbols = "".join(random.choice("@&#$%^*!") for _ in range(3)) # শেষে ৩টি সিম্বল ফিক্সড
    return f"{random_part}{symbols}"

# --- ইনলাইন বাটন ক্লিকের লজিক (কালারফুল বাটন সিস্টেমসহ) ---
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # পাসওয়ার্ড জেনারেশন (কালারফুল সিলেকশন)
    if "set_date" in data:
        # সিলেক্ট করা বাটন Green, বাকিগুলো Red
        keyboard = [
            [InlineKeyboardButton("✅ Date+👑 (Green)", callback_data="set_date_pass"), 
             InlineKeyboardButton("❌ Symbol+👑 (Red)", callback_data="set_sym_pass"), 
             InlineKeyboardButton("❌ Alphabet (Red)", callback_data="set_alpha_pass")],
            [InlineKeyboardButton("🔄 Generate New 🔄", callback_data="regen_date_pass")]
        ]
        # পাসওয়ার্ড জেনারেট করে মেসেজ এডিট করুন... (এখানে আপনার পাসওয়ার্ড জেনারেটর কল করুন)
        await query.edit_message_text(f"🔒 Password: `{generate_date_random_password()}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif "set_sym" in data:
        # সিম্বল বাটন Green, বাকিগুলো Red
        keyboard = [
            [InlineKeyboardButton("❌ Date+👑 (Red)", callback_data="set_date_pass"), 
             InlineKeyboardButton("✅ Symbol+👑 (Green)", callback_data="set_sym_pass"), 
             InlineKeyboardButton("❌ Alphabet (Red)", callback_data="set_alpha_pass")],
            [InlineKeyboardButton("🔄 Generate New 🔄", callback_data="regen_sym_pass")]
        ]
        await query.edit_message_text(f"🔒 Password: `{generate_symbol_random_password()}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif "set_alpha" in data:
        keyboard = [
            [InlineKeyboardButton("❌ Date+👑 (Red)", callback_data="set_date_pass"), 
             InlineKeyboardButton("❌ Symbol+👑 (Red)", callback_data="set_sym_pass"), 
             InlineKeyboardButton("✅ Alphabet (Green)", callback_data="set_alpha_pass")],
            [InlineKeyboardButton("🔄 Generate New 🔄", callback_data="regen_alpha_pass")]
        ]
        await query.edit_message_text(f"🔒 Password: `{generate_only_alphabet_password()}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# বাকি কোডগুলো আগের মতোই থাকবে...
