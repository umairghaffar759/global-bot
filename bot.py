import telebot
from telebot import types
import os
import time
from flask import Flask
from threading import Thread

# --- Render Fake Server ---
app = Flask('')
@app.route('/')
def home(): return "Global Chat Bot is Live!"

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

# Storage (Ab isay behtar tareeqe se handle kiya hai)
waiting_users = [] 
active_chats = {}  
user_data = {} 
chat_start_time = {}
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
    return markup

# --- Fixed Stop Logic ---
def end_chat(user_id):
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        chat_start_time.pop(user_id, None)
        chat_start_time.pop(partner_id, None)
        
        # Dono ko menu dikhana lazmi hai
        bot.send_message(user_id, "🛑 Chat ended.", reply_markup=main_menu())
        bot.send_message(partner_id, "🛑 Your partner disconnected.", reply_markup=main_menu())
        return True
    return False

# --- Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌍 *Welcome!* Click '🔍 Find Partner' to start.", 
                     parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🛑 Stop Current Dialog")
def stop_button_handler(message):
    if not end_chat(message.chat.id):
        if message.chat.id in waiting_users:
            waiting_users.remove(message.chat.id)
            bot.send_message(message.chat.id, "🔍 Search cancelled.", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "You are not in a chat.", reply_markup=main_menu())

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
        if user_id not in waiting_users:
            waiting_users.append(user_id)
        bot.send_message(user_id, "🔍 Searching for a partner...")

# --- Message Relay (Isay sabse niche rakha hai taaki commands pehle check hon) ---
@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = message.chat.id
    # Agar user chat mein hai, toh message bhejien
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            bot.send_message(partner_id, message.text)
        except:
            end_chat(user_id)
    else:
        bot.send_message(user_id, "Welcome! Type /start or use buttons.", reply_markup=main_menu())

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)