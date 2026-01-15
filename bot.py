import telebot
import sqlite3
import os
from flask import Flask
from threading import Thread

# --- Fake Server for Render ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render automatically provides a PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Your Bot Logic ---
TOKEN = '8336091114:AAHhPYuOygY3URO05RKTjPmv0LtapJiYHRE'
ADMIN_ID = 8320339730
bot = telebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect('global.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, partner_id INTEGER, status TEXT, coins INTEGER DEFAULT 10)')
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    init_db()
    bot.send_message(message.chat.id, "🌍 *Welcome to Global Chat!*")

# ... (Baki purana matching logic yahan rahega)

if __name__ == '__main__':
    init_db()
    keep_alive() # Isse Render ka port error khatam ho jayega
    print("Bot is starting...")
    bot.infinity_polling()