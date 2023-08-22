
import logging
import json
import base64
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Charger les données du fichier drugs.json avec l'encodage correct
with open("data/drugs.json", "r", encoding="utf-8") as file:
    drugs_data = json.load(file)

def encode_key(key):
    return base64.b64encode(key.encode()).decode()

def decode_key(encoded_key):
    return base64.b64decode(encoded_key.encode()).decode()

def generate_keyboard(data, prefix=""):
    keyboard = [[InlineKeyboardButton(k, callback_data=prefix + encode_key(k))] for k in data.keys()]
    return InlineKeyboardMarkup(keyboard)

def start(update, context):
    keyboard = generate_keyboard(drugs_data)
    update.message.reply_text('Choisissez une catégorie:', reply_markup=keyboard)

def button(update, context):
    query = update.callback_query
    query.answer()
    
    current_data_encoded = query.data
    next_data = drugs_data
    for encoded_key in current_data_encoded.split("/"):
        key = decode_key(encoded_key)
        if key in next_data:
            next_data = next_data[key]
        else:
            query.edit_message_text(text="Erreur: Catégorie non trouvée.")
            return

    if next_data:
        keyboard = generate_keyboard(next_data, current_data_encoded + "/")
        query.edit_message_text(text=f"Vous avez sélectionné {key}. Choisissez une sous-catégorie:", reply_markup=keyboard)
    else:
        query.edit_message_text(text=f"Vous avez sélectionné {key}. Aucune sous-catégorie disponible.")

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
