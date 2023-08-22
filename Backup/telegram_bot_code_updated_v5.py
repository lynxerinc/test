
import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Charger les données du fichier drugs.json
with open("data/drugs.json", "r") as file:
    drugs_data = json.load(file)

def generate_keyboard(data):
    keyboard = [[InlineKeyboardButton(k, callback_data=k)] for k in data.keys()]
    return InlineKeyboardMarkup(keyboard)

def start(update, context):
    keyboard = generate_keyboard(drugs_data)
    update.message.reply_text('Choisissez une catégorie:', reply_markup=keyboard)

def button(update, context):
    query = update.callback_query
    query.answer()
    
    current_data = query.data
    next_data = drugs_data
    for key in current_data.split("/"):
        if key in next_data:
            next_data = next_data[key]
        else:
            query.edit_message_text(text="Erreur: Catégorie non trouvée.")
            return

    if next_data:
        keyboard = generate_keyboard(next_data)
        query.edit_message_text(text=f"Vous avez sélectionné {current_data}. Choisissez une sous-catégorie:", reply_markup=keyboard)
    else:
        query.edit_message_text(text=f"Vous avez sélectionné {current_data}. Aucune sous-catégorie disponible.")

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
