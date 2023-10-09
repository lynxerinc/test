# Importations
import logging
import json
import secrets
import random
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les données depuis un fichier JSON
with open("user_messages.json", "r", encoding="utf-8") as file:
    user_messages = json.load(file)

# Charger les données du fichier drugs.json avec l'encodage correct
drugs_data = json.load(open("data/drugs.json"))

# Initialisation des variables globales
user_carts = {}
user_message_ids = {}
id_to_data = {}
data_to_id = {}
current_id = 0

# Fonctions
def read_json_file(filename_or_url, key=None, default_value=None):
    try:
        if filename_or_url.startswith("http"):
            response = requests.get(filename_or_url)
            if response.status_code == 200:
                data = response.json()
            else:
                return default_value
        else:
            with open(filename_or_url, "r", encoding="utf-8") as file:
                data = json.load(file)
        
        return data.get(key, default_value) if key else data
    except FileNotFoundError:
        return default_value

def read_bot_status():
    return read_json_file('bot_status_url', key='is_open', default_value=True)

def send_closure_message(context, chat_id):
    message = user_messages.get("closure_message", "")
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def get_username(update):
    user = update.effective_user
    return user.username if user and user.username else "no user"

# Add other required functions here...

def button(update, context):
    query = update.callback_query
    
    if query.data == "clear_cart":
        clear_cart(update, context)
    elif query.data == "cart":
        display_cart(update, context)
    
    query.answer()

# Add other logic and functions as needed...

def main():
    updater = Updater(token='6140284584:AAF8gviWzKMkHEn5TktrVMral7PPMW7uxXk', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
