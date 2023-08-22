
import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Charger les données du fichier drugs.json avec l'encodage correct
with open("data/drugs.json", "r", encoding="utf-8") as file:
    drugs_data = json.load(file)

id_to_data = {}
data_to_id = {}
current_id = 0

def generate_ids(data, prefix=""):
    global current_id
    local_ids = {}
    for key, value in data.items():
        current_key = prefix + key
        current_id += 1
        local_ids[current_key] = current_id
        id_to_data[current_id] = current_key
        data_to_id[current_key] = current_id
        if isinstance(value, dict):
            generate_ids(value, current_key + "/")
    return local_ids

generate_ids(drugs_data)

def generate_keyboard(data, prefix=""):
    keyboard = []
    for key in data.keys():
        current_key = prefix + key
        button_id = data_to_id[current_key]
        keyboard.append([InlineKeyboardButton(key, callback_data=str(button_id))])
    return InlineKeyboardMarkup(keyboard)

def start(update, context):
    keyboard = generate_keyboard(drugs_data)
    update.message.reply_text('Choisissez une catégorie:', reply_markup=keyboard)

def button(update, context):
    query = update.callback_query
    query.answer()
    
    button_id = int(query.data)
    current_key = id_to_data[button_id]
    keys = current_key.split("/")
    
    next_data = drugs_data
    for key in keys:
        next_data = next_data[key]

    if next_data:
        keyboard = generate_keyboard(next_data, current_key + "/")
        query.edit_message_text(text=f"Vous avez sélectionné {keys[-1]}. Choisissez une sous-catégorie:", reply_markup=keyboard)
    else:
        query.edit_message_text(text=f"Vous avez sélectionné {keys[-1]}. Aucune sous-catégorie disponible.")

def main():
    # (Vous devriez remplacer 'YOUR_TOKEN' par votre véritable token de bot Telegram)
    updater = Updater(token='5938970819:AAGH21yb_8MEn3HieRRJ-4B1wNrDhIzLzHU', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
