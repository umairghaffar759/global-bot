import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- Render Fake Server ---
app = Flask('')
@app.route('/')
def home(): return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run); t.start()

# --- Bot Setup ---
TOKEN = '8336091114:AAHhPYuOygY3URO05RKTjPmv0LtapJiYHRE'
ADMIN_ID = 8320339730
bot = telebot.TeleBot(TOKEN)

waiting_users = [] 
active_chats = {}  

# --- Main Menu Keyboard ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 Find Partner")
    markup.row("👤 Select Gender", "💎 Become a VIP")
    markup.row("📜 Rules", "❓ How to use")
    return markup

def chat_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛑 Stop Current Dialog")
    markup.row("🔄 Stop & Find New Partner")
    return markup

# --- Handlers ---

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = "🌍 *Welcome to Global Anonymous Chat!*\n\nInteracting with strangers has never been easier. Use the buttons below to start."
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🔍 Find Partner")
def search_handler(message):
    user_id = message.chat.id
    if user_id in active_chats:
        bot.send_message(user_id, "❌ You are already in a chat!")
        return
    
    if user_id in waiting_users:
        bot.send_message(user_id, "🔍 Still searching... please wait.")
    else:
        if waiting_users:
            partner_id = waiting_users.pop(0)
            active_chats[user_id] = partner_id
            active_chats[partner_id] = user_id
            bot.send_message(user_id, "✅ Partner found! Start chatting.", reply_markup=chat_menu())
            bot.send_message(partner_id, "✅ Partner found! Start chatting.", reply_markup=chat_menu())
        else:
            waiting_users.append(user_id)
            bot.send_message(user_id, "🔍 Searching for a global partner...")

@bot.message_handler(func=lambda m: m.text in ["🛑 Stop Current Dialog", "🔄 Stop & Find New Partner"])
def stop_handler(message):
    user_id = message.chat.id
    find_new = "New Partner" in message.text
    
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        bot.send_message(user_id, "🛑 Chat ended.", reply_markup=main_menu())
        bot.send_message(partner_id, "🛑 Your partner disconnected.", reply_markup=main_menu())
        if find_new: search_handler(message)
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "🔍 Search cancelled.", reply_markup=main_menu())
    else:
        bot.send_message(user_id, "You are not in a chat.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "💎 Become a VIP")
def vip_handler(message):
    text = "💎 *VIP Benefits:*\n• No Ads\n• Priority Matching\n• Gender Filter\n\n💳 *Payment Support:*\nContact @admin to buy VIP for only $5/Lifetime."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 Select Gender")
def gender_handler(message):
    bot.send_message(message.chat.id, "⚠️ Gender filter is a **VIP Feature**. Upgrade to use this!")

@bot.message_handler(func=lambda m: m.text == "📜 Rules")
def rules(message):
    bot.send_message(message.chat.id, "1. No spamming\n2. Be respectful\n3. English only\n4. No sharing personal data.")

@bot.message_handler(func=lambda m: m.text == "❓ How to use")
def how_to(message):
    bot.send_message(message.chat.id, "Just click 'Find Partner' and we will connect you to a random stranger worldwide!")

@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = message.chat.id
    if user_id in active_chats:
        bot.send_message(active_chats[user_id], message.text)

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()