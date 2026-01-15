import telebot
from telebot import types
import os
import time
from flask import Flask
from threading import Thread

# --- Render Fake Server (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is alive and running!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run); t.start()

# --- Bot Configuration ---
TOKEN = '8336091114:AAHhPYuOygY3URO05RKTjPmv0LtapJiYHRE'
ADMIN_ID = 8320339730
USDT_ADDRESS = "TJWBb9M33WghHpWwMpRRacEy4eCcFS65Pb" # Aapka verified address

bot = telebot.TeleBot(TOKEN)

# In-memory storage (Restart hone par clear ho jayega)
waiting_users = [] 
active_chats = {}  
user_start_time = {} # Trial monitoring: {user_id: timestamp}

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

# --- Helper Functions ---
def is_trial_over(user_id):
    if user_id not in user_start_time:
        user_start_time[user_id] = time.time()
        return False
    
    # 1 Hour = 3600 seconds
    elapsed = time.time() - user_start_time[user_id]
    if elapsed > 3600:
        return True
    return False

# --- Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "🌍 *Welcome to Global Anonymous Chat!*\n\n"
        "🎁 *Free Trial:* 1 Hour every day.\n"
        "💎 *VIP Status:* Unlimited chat & gender filter."
    )
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔍 Find Partner")
def search_handler(message):
    user_id = message.chat.id
    
    if is_trial_over(user_id):
        text = "⚠️ *Trial Expired!*\n\nAapka aaj ka 1 ghanta khatam ho chuka hai. Mazeed chatting ke liye VIP plan lein."
        bot.send_message(user_id, text, parse_mode="Markdown")
        return vip_handler(message)

    if user_id in active_chats:
        bot.send_message(user_id, "❌ Already in a chat!")
        return
    
    if user_id in waiting_users:
        bot.send_message(user_id, "🔍 Searching... please wait.")
    else:
        if waiting_users:
            partner_id = waiting_users.pop(0)
            active_chats[user_id] = partner_id
            active_chats[partner_id] = user_id
            bot.send_message(user_id, "✅ Partner found! Start talking.", reply_markup=chat_menu())
            bot.send_message(partner_id, "✅ Partner found! Start talking.", reply_markup=chat_menu())
        else:
            waiting_users.append(user_id)
            bot.send_message(user_id, "🔍 Searching for a global partner...")

@bot.message_handler(func=lambda m: m.text == "🛑 Stop Current Dialog")
def stop_handler(message):
    user_id = message.chat.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        bot.send_message(user_id, "🛑 Chat ended.", reply_markup=main_menu())
        bot.send_message(partner_id, "🛑 Your partner disconnected.", reply_markup=main_menu())
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "🔍 Search cancelled.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💎 Become a VIP")
def vip_handler(message):
    plans = (
        "💎 *VIP SUBSCRIPTION PLANS*\n\n"
        "1️⃣ **Weekly Plan**\n"
        "• 100 Stars OR $1.99\n\n"
        "2️⃣ **Monthly Plan**\n"
        "• 250 Stars OR $5.00\n\n"
        "3️⃣ **Yearly Plan**\n"
        "• 4000 Stars OR $79.99\n\n"
        "🏦 **USDT (TRC-20) Address:**\n"
        f"`{USDT_ADDRESS}`\n\n"
        "⚠️ *Note:* Payment bhej kar screenshot @admin ko send karein activation ke liye."
    )
    bot.send_message(message.chat.id, plans, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 My Profile")
def profile(message):
    user_id = message.chat.id
    bot.send_message(user_id, f"👤 **Profile Info**\n\nID: `{user_id}`\nStatus: Free (Trial Active)", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = message.chat.id
    if user_id in active_chats:
        try:
            bot.send_message(active_chats[user_id], message.text)
        except:
            stop_handler(message)

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()