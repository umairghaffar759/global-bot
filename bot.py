import telebot
import sqlite3

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
    bot.send_message(message.chat.id, "🌍 *Welcome to Global Chat!*\n\nYou have 10 free messages. Buy premium for unlimited.", parse_mode="Markdown")

# Baki matching logic jo maine pehle di thi wo yahan fit hogi...
bot.infinity_polling()