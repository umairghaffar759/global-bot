import telebot
from telebot import types
import os
import time
from flask import Flask
from threading import Thread

# --- Render Fake Server (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Global Chat Bot is Live!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run); t.start()

# --- Bot Configuration ---
TOKEN = '8336091114:AAHhPYuOygY3URO05RKTjPmv0LtapJiYHRE'
ADMIN_ID = 8320339730
USDT_ADDRESS = "TJWBb9M33WghHpWwMpRRacEy4eCcFS65Pb"

bot = telebot.TeleBot(TOKEN)

# In-memory storage
waiting_users = [] 
active_chats = {}  
user_start_time = {} 

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
    markup.row("🔄 Stop & Find New")
    return markup

# --- Functions ---
def is_trial_over(user_id):
    if user_id not in user_start_time:
        user_start_time[user_id] = time.time()
        return False
    elapsed = time.time() - user_start_time[user_id]
    if elapsed > 3600: # 1 Hour trial
        return True
    return False

# --- Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "🌍 *Welcome to Global Anonymous Chat!*\n\n"
        "Connect with strangers worldwide instantly. 🕵️‍♂️\n\n"
        "🎁 *Trial:* 1 Hour free every day.\n"
        "📜 *Agreement:* By using this bot, you agree to our Rules.\n\n"
        "Use the buttons below to start!"
    )
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔍 Find Partner")
def search_handler(message):
    user_id = message.chat.id
    if is_trial_over(user_id):
        bot.send_message(user_id, "⚠️ *Trial Expired!*\nYour 1-hour daily limit is over. Please upgrade to VIP.", parse_mode="Markdown")
        return vip_handler(message)
    
    if user_id in active_chats:
        bot.send_message(user_id, "❌ You are already in a chat!")
        return

    if waiting_users:
        if user_id in waiting_users: return
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        bot.send_message(user_id, "✅ Partner found! Be respectful.", reply_markup=chat_menu())
        bot.send_message(partner_id, "✅ Partner found! Be respectful.", reply_markup=chat_menu())
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "🔍 Searching for a partner...")

@bot.message_handler(func=lambda m: m.text in ["🛑 Stop Current Dialog", "🔄 Stop & Find New"])
def stop_handler(message):
    user_id = message.chat.id
    find_new = "New" in message.text
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        bot.send_message(user_id, "🛑 Chat ended.", reply_markup=main_menu())
        bot.send_message(partner_id, "🛑 Partner disconnected.", reply_markup=main_menu())
        if find_new: search_handler(message)
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "🔍 Search cancelled.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📜 Rules")
def rules(message):
    rules_text = (
        "⚖️ **Chat Rules**\n\n"
        "1️⃣ **No Bullying:** Be kind to strangers.\n"
        "2️⃣ **No Spam:** Don't send ads or repetitive texts.\n"
        "3️⃣ **No NSFW:** Pornography = Permanent Ban.\n"
        "4️⃣ **Privacy:** Never share your phone/social media.\n"
        "5️⃣ **Language:** Use English for global matching."
    )
    bot.send_message(message.chat.id, rules_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 Become a VIP")
def vip_handler(message):
    plans = (
        "💎 **VIP SUBSCRIPTION PLANS**\n\n"
        "1️⃣ *Weekly:* 100 Stars / $1.99\n"
        "2️⃣ *Monthly:* 250 Stars / $5.00\n"
        "3️⃣ *Yearly:* 4000 Stars / $79.99\n\n"
        "🏦 **USDT (TRC-20) Address:**\n"
        f"`{USDT_ADDRESS}`\n\n"
        "Payment bhej kar screenshot @admin ko send karein."
    )
    bot.send_message(message.chat.id, plans, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "❓ How to use")
def how_to(message):
    bot.send_message(message.chat.id, "Click '🔍 Find Partner' to match. Use '🛑 Stop' to end. Simple!")

@bot.message_handler(func=lambda m: m.text == "👤 My Profile")
def profile(message):
    bot.send_message(message.chat.id, f"👤 **Profile Info**\n\nID: `{message.chat.id}`\nStatus: Free User", parse_mode="Markdown")

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, "👨‍💻 Admin Panel: Use /broadcast [text] for ads.")

@bot.message_handler(func=lambda message: True)
def relay(message):
    if message.chat.id in active_chats:
        bot.send_message(active_chats[message.chat.id], message.text)

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()