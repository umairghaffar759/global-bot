import telebot
from telebot import types
import os
import time
from flask import Flask
from threading import Thread

# --- Render Fake Server ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run); t.start()

# --- Bot Setup ---
TOKEN = '8336091114:AAHhPYuOygY3URO05RKTjPmv0LtapJiYHRE'
ADMIN_ID = 8320339730
USDT_ADDRESS = "TJWBb9M33WghHpWwMpRRacEy4eCcFS65Pb"

bot = telebot.TeleBot(TOKEN)

# Data Storage
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

# --- Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in user_data:
        bot.send_message(user_id, "👋 *Welcome!* Please select your gender to continue:", 
                         parse_mode="Markdown", reply_markup=gender_markup())
    else:
        bot.send_message(user_id, "🌍 *Welcome Back!* Click 'Find Partner' to start.", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_g_'))
def set_gender(call):
    user_id = call.message.chat.id
    gender = call.data.split('_')[2]
    user_data[user_id] = {'gender': gender, 'is_vip': False}
    bot.edit_message_text("✅ Gender set! Now please enter your **Age** (e.g., 20):", 
                          user_id, call.message.message_id)
    bot.register_next_step_handler(call.message, get_age)

def get_age(message):
    user_id = message.chat.id
    if message.text.isdigit():
        user_data[user_id]['age'] = int(message.text)
        bot.send_message(user_id, "🧐 Who are you looking for?", reply_markup=looking_for_markup())
    else:
        bot.send_message(user_id, "❌ Please enter a valid number for age:")
        bot.register_next_step_handler(message, get_age)

@bot.callback_query_handler(func=lambda call: call.data.startswith('look_'))
def set_looking_for(call):
    user_id = call.message.chat.id
    looking_for = call.data.split('_')[1]
    user_data[user_id]['looking_for'] = looking_for
    bot.edit_message_text(f"✅ All set! You are looking for a {looking_for}.", user_id, call.message.message_id)
    bot.send_message(user_id, "You can now use the bot!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔍 Find Partner")
def search_handler(message):
    user_id = message.chat.id
    
    # VIP Filter Logic
    data = user_data.get(user_id, {})
    if not data.get('is_vip', False):
        bot.send_message(user_id, "⚠️ *VIP Feature:* Selection based matching (Male/Female filter) is only for VIP members.\n\n"
                                 "Normal users are matched randomly with anyone.", parse_mode="Markdown")
        # Yahan normal random matching logic chalegi
    
    # Matching Logic (Random for now, VIP logic can be added later)
    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        chat_start_time[user_id] = time.time()
        chat_start_time[partner_id] = time.time()
        bot.send_message(user_id, "✅ Partner found!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("🛑 Stop Current Dialog"))
        bot.send_message(partner_id, "✅ Partner found!", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("🛑 Stop Current Dialog"))
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "🔍 Searching...")

@bot.message_handler(func=lambda m: m.text == "💎 Become a VIP")
def vip_handler(message):
    plans = (f"💎 **VIP BENEFITS:**\n• Search by Gender (Male/Female)\n• No 1-Hour Limit\n• Exclusive Badge\n\n"
             f"🏦 **USDT (TRC-20):**\n`{USDT_ADDRESS}`\n\nSend screenshot to @admin to activate!")
    bot.send_message(message.chat.id, plans, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = message.chat.id
    if user_id in active_chats:
        bot.send_message(active_chats[user_id], message.text)

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()