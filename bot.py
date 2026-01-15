import telebot
from telebot import types
import os
import time
from flask import Flask
from threading import Thread

# --- Render Fake Server (Keep Alive) ---
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
user_data = {} # {user_id: {'gender': 'M', 'age': 20, 'looking_for': 'F', 'is_vip': False}}
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

def gender_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Male 👨", callback_data="set_g_M"),
               types.InlineKeyboardButton("Female 👩", callback_data="set_g_F"))
    return markup

def looking_for_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Male 👨", callback_data="look_M"),
               types.InlineKeyboardButton("Female 👩", callback_data="look_F"))
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

# --- Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in user_data:
        bot.send_message(user_id, "👋 *Welcome!* Please select your gender:", 
                         parse_mode="Markdown", reply_markup=gender_markup())
    else:
        bot.send_message(user_id, "🌍 *Global Chat Menu*", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_g_'))
def set_gender(call):
    user_id = call.message.chat.id
    gender = call.data.split('_')[2]
    user_data[user_id] = {'gender': gender, 'is_vip': False}
    bot.edit_message_text("✅ Gender set! Now type your **Age** (e.g. 22):", 
                          user_id, call.message.message_id)
    bot.register_next_step_handler(call.message, get_age)

def get_age(message):
    user_id = message.chat.id
    if message.text.isdigit():
        user_data[user_id]['age'] = int(message.text)
        bot.send_message(user_id, "🧐 Who are you looking for?", reply_markup=looking_for_markup())
    else:
        bot.send_message(user_id, "❌ Please enter a number for age:")
        bot.register_next_step_handler(message, get_age)

@bot.callback_query_handler(func=lambda call: call.data.startswith('look_'))
def set_looking_for(call):
    user_id = call.message.chat.id
    user_data[user_id]['looking_for'] = call.data.split('_')[1]
    bot.edit_message_text("✅ Profile Completed!", user_id, call.message.message_id)
    bot.send_message(user_id, "Use 'Find Partner' to start chatting!", reply_markup=main_menu())

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
        bot.send_message(user_id, "❌ Already in chat!")
        return
    
    # VIP Requirement Check
    if not user_data.get(user_id, {}).get('is_vip', False):
        bot.send_message(user_id, "⚠️ *Note:* Gender filter is a 💎 VIP feature. Normal users match randomly.", parse_mode="Markdown")

    if waiting_users:
        if user_id in waiting_users: return
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        chat_start_time[user_id] = time.time()
        chat_start_time[partner_id] = time.time()
        bot.send_message(user_id, "✅ Partner found! No @usernames allowed.", reply_markup=chat_menu())
        bot.send_message(partner_id, "✅ Partner found! No @usernames allowed.", reply_markup=chat_menu())
    else:
        if user_id not in waiting_users: waiting_users.append(user_id)
        bot.send_message(user_id, "🔍 Searching...")

@bot.message_handler(func=lambda m: m.text == "📜 Rules")
def rules_handler(message):
    bot.send_message(message.chat.id, "⚖️ **Rules:**\n1. No @usernames\n2. No NSFW\n3. Wait 1 min for links.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 Become a VIP")
def vip_handler(message):
    bot.send_message(message.chat.id, f"💎 **VIP Status**\nWeekly: $1.99\n\n🏦 **USDT (TRC-20):**\n`{USDT_ADDRESS}`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = message.chat.id
    if user_id in active_chats:
        text = message.text.lower()
        # 1. Block Usernames
        if "@" in text:
            bot.send_message(user_id, "❌ Usernames are blocked for safety!")
            return
        # 2. Link Timer (1 Minute)
        if "t.me/" in text or "telegram.me/" in text:
            elapsed = time.time() - chat_start_time.get(user_id, 0)
            if elapsed < 60:
                bot.send_message(user_id, f"⏳ Wait {int(60-elapsed)}s more to send links.")
                return
        
        try:
            bot.send_message(active_chats[user_id], message.text)
        except:
            end_chat(user_id)
    else:
        bot.send_message(user_id, "Click a button to start.", reply_markup=main_menu())

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(timeout=60)