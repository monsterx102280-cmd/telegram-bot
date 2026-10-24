import telebot
from telebot import types
import sqlite3
import datetime

BOT_TOKEN = "8990625815:AAHISN6kfj5C2AM2n1O4uHaw9wOayr705Qs"
ADMIN_ID = 8544725514 

bot = telebot.TeleBot(BOT_TOKEN)

def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes (user_id INTEGER, note TEXT)''')
    conn.commit()
    conn.close()

init_db()

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('Calculator')
    btn2 = types.KeyboardButton('My Notes')
    btn3 = types.KeyboardButton('Date & Time')
    btn4 = types.KeyboardButton('My Info')
    btn5 = types.KeyboardButton('Help')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = f"Welcome {message.from_user.first_name}!\nI am your personal assistant. Choose an option below."
    bot.reply_to(message, text, reply_markup=main_menu())
    
    if message.from_user.id != ADMIN_ID:
        bot.send_message(ADMIN_ID, f"New user: {message.from_user.first_name}\nID: {message.from_user.id}")

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    
    if text == 'Calculator':
        msg = bot.reply_to(message, "Enter math (e.g., 5+5*2):")
        bot.register_next_step_handler(msg, process_calc)
        
    elif text == 'My Notes':
        show_notes(message)
        
    elif text == 'Date & Time':
        now = datetime.datetime.now()
        bot.reply_to(message, f"Date: {now.strftime('%d-%m-%Y')}\nTime: {now.strftime('%I:%M %p')}")
        
    elif text == 'My Info':
        bot.reply_to(message, f"Name: {message.from_user.first_name}\nID: {message.from_user.id}\nUsername: @{message.from_user.username}")
        
    elif text == 'Help':
        bot.reply_to(message, "1. Use Calculator for math.\n2. Type anything to save as a note.\n3. Use My Notes to view saved notes.")
        
    else:
        if len(text) > 2:
            save_note(message.from_user.id, text)
            bot.reply_to(message, "Saved as a note! Check 'My Notes'.")
        else:
            bot.reply_to(message, "Please choose an option from the menu.")

def process_calc(message):
    try:
        allowed = "0123456789+-*/(). "
        if not all(c in allowed for c in message.text):
            bot.reply_to(message, "Only numbers and + - * / are allowed.")
            return
        result = eval(message.text)
        bot.reply_to(message, f"Result: {result}", reply_markup=main_menu())
    except:
        bot.reply_to(message, "Invalid math. Try again.", reply_markup=main_menu())

def save_note(user_id, text):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO notes (user_id, note) VALUES (?, ?)", (user_id, text))
    conn.commit()
    conn.close()

def show_notes(message):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute("SELECT note FROM notes WHERE user_id=?", (message.from_user.id,))
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        bot.reply_to(message, "You have no notes.")
    else:
        notes_text = "Your Notes:\n\n"
        for i, row in enumerate(rows, 1):
            notes_text += f"{i}. {row[0]}\n"
        bot.reply_to(message, notes_text)

print("Bot started...")
bot.infinity_polling()
