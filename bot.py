import telebot
import os
from flask import Flask
from threading import Thread

# --- Render Fake Server ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot Setup ---
TOKEN = '8336091114:AAHhPYuOygY3URO05RKTjPmv0LtapJiYHRE'
bot = telebot.TeleBot(TOKEN)

# Simple Memory-based tracking (Taaki file ka masla na ho)
waiting_users = [] # [user_id1, user_id2]
active_chats = {}  # {user_id: partner_id}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🌍 *Welcome to Global Anonymous Chat!*\n\nType /search to find a stranger (English Only).", parse_mode="Markdown")

@bot.message_handler(commands=['search'])
def search(message):
    user_id = message.chat.id
    
    if user_id in active_chats:
        bot.send_message(user_id, "❌ You are already in a chat! Use /stop first.")
        return

    if user_id in waiting_users:
        bot.send_message(user_id, "🔍 Still searching... please wait.")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        
        bot.send_message(user_id, "✅ Partner found! Start chatting in English.")
        bot.send_message(partner_id, "✅ Partner found! Start chatting in English.")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "🔍 Searching for a global partner...")

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.chat.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        bot.send_message(user_id, "🛑 Chat ended.")
        bot.send_message(partner_id, "🛑 Your partner has disconnected.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "🔍 Search cancelled.")
    else:
        bot.send_message(user_id, "You are not in a chat.")

@bot.message_handler(func=lambda message: True)
def relay(message):
    user_id = message.chat.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            bot.send_message(partner_id, message.text)
        except:
            bot.send_message(user_id, "⚠️ Partner is unavailable.")
    else:
        bot.send_message(user_id, "Welcome! Type /search to start.")

if __name__ == '__main__':
    keep_alive()
    print("Bot is starting...")
    bot.infinity_polling()