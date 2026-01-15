import telebot
from telebot import types
import os
import time
from flask import Flask
from threading import Thread

# --- Render Fake Server ---
app = Flask('')
@app.route('/')
def home(): return "Global Bot is Online!"

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run); t.start()

# --- Bot Setup ---
TOKEN = '8336091114:AAHhPYuOygY3URO05RKTjPmv0LtapJiYHRE'
ADMIN_ID = 8320339730
USDT_ADDRESS = "TJWBb9M33WghHpWwMpRRacEy4eCcFS65Pb"

bot = telebot.TeleBot(TOKEN)

# Storage
waiting_users = [] 
active_chats = {}  
chat_start_time = {}

# --- Keyboards ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 Find Partner")
    markup.row("💎 Become a VIP", "👤 My Profile")
    markup.row("📜 Rules", "❓ How to use")
    return markup

def chat_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛑 Stop Current Dialog")
    return markup

# --- Functions ---
def end_chat(user_id):
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        chat_start_time.pop(user_id, None)
        chat_start_time.pop(partner_id, None)
        bot.send_message(user_id, "🛑 Chat ended.", reply_markup=main_menu())
        bot.send_message(partner_id, "🛑 Your partner disconnected.", reply_markup=main_menu())
        return True
    return False

# --- Priority Handlers (Pehle ye check honge) ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌍 *Welcome!* Click '🔍 Find Partner' to start.", 
                     parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛑 Stop Current Dialog")
def stop_handler(message):
    if not end_chat(message.chat.id):
        if message.chat.id in waiting_users:
            waiting_users.remove(message.chat.id)
            bot.send_message(message.chat.id, "🔍 Search cancelled.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔍 Find Partner")
def search_handler(message):
    user_id = message.chat.id
    if user_id in active_chats:
        bot.send_message(user_id, "❌ You are already in a chat!")
        return
    if waiting_users:
        if user_id in waiting_users: return
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        chat_start_time[user_id] = time.time()
        bot.send_message(user_id, "✅ Partner found!", reply_markup=chat_menu())
        bot.send_message(partner_id, "✅ Partner found!", reply_markup=chat_menu())
    else:
        if user_id not in waiting_users: waiting_users.append(user_id)
        bot.send_message(user_id, "🔍 Searching for a partner...")

@bot.message_handler(func=lambda m: m.text == "📜 Rules")
def rules_handler(message):
    text = "⚖️ **Rules:**\n1. No Spam\n2. Be Respectful\n3. No NSFW content."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 Become a VIP")
def vip_handler(message):
    text = f"💎 **VIP Plans:**\n$5/Month\n\n🏦 **USDT (TRC-20):**\n`{USDT_ADDRESS}`"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "❓ How to use")
def how_to(message):
    bot.send_message(message.chat.id, "Simply click 'Find Partner' and wait for a match!")

@bot.message_handler(func=lambda m: m.text == "👤 My Profile")
def profile_handler(message):
    bot.send_message(message.chat.id, f"👤 **ID:** `{message.chat.id}`\nStatus: Free")

# --- Catch-All Relay (Ye sabse aakhir mein hona chahiye) ---
@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = message.chat.id
    if user_id in active_chats:
        bot.send_message(active_chats[user_id], message.text)
    else:
        # Agar user chat mein nahi hai aur koi command nahi di, tab ye message aye
        bot.send_message(user_id, "Welcome! Type /start to see the menu.", reply_markup=main_menu())

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)