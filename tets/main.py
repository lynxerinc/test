import json
import logging
import requests
import time
from datetime import datetime
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Importations des modules
from cart_management import add_to_cart, clear_cart, delete_product, delete_specific_product, display_cart, generate_ids, user_carts, user_message_ids, id_to_data, data_to_id
from checkout_process import handle_checkout, generate_unique_id
from error_handling import handle_general_error
from payment_methods import handle_payment_method
from user_interaction import get_username, generate_keyboard, dynamic_access, read_bot_status, read_json_file, extract_price

# Charger les données du fichier constants.json avec l'encodage correct
with open("constants.json", "r", encoding="utf-8") as file:
    constants = json.load(file)

# Charger les données du fichier drugs.json avec l'encodage correct
with open("data/drugs.json", "r", encoding="utf-8") as file:
    drugs_data = json.load(file)

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Génération des IDs pour le clavier
generate_ids(drugs_data)

# Fonctions principales
def start(update, context):
    logger.info("Fonction start appelée")
    if not read_bot_status():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Le bot est actuellement fermé.")
        return

    user_id = update.effective_user.id
    username = get_username(update)
    
    logger.info(f"Nom d'utilisateur récupéré : {username}")

    # Log ajouté avant l'appel à generate_keyboard
    logger.info("Appel de generate_keyboard")
    keyboard = generate_keyboard(drugs_data)

    context.bot.send_message(chat_id=update.effective_chat.id, text='Choisissez une catégorie :', reply_markup=keyboard)


def button(update, context):
    query = update.callback_query

    if query.data == "clear_cart":
        clear_cart(update, context)
        return
    
    elif query.data == "cart":
        display_cart(update, context)
        return
    
    elif query.data == "delete_products":
        delete_specific_product(update, context)
        return

    elif query.data == "checkout":
        handle_checkout(update, context)
    
    elif query.data.startswith("payment_"):
        payment_method = query.data.split("_")[1]
        handle_payment_method(update, context, payment_method)

    else:
        try:
            button_id = int(query.data)
        except ValueError:
            if query.data.startswith("delete_product:"):
                product_to_delete = query.data.split(":")[1]
                delete_product(update, context, product_to_delete)
                return

        query.answer()

        if button_id == -1:
            keyboard = generate_keyboard(drugs_data)
            query.edit_message_text(text="Choisissez une catégorie:", reply_markup=keyboard)
            return

        current_key = id_to_data[button_id]
        keys = current_key.split("/")

        next_data = dynamic_access(drugs_data, keys)

        back_data = "-1" if len(keys) == 1 else str(data_to_id["/".join(keys[:-1])])

        if isinstance(next_data, dict):
            keyboard = generate_keyboard(next_data, current_key + "/")
            query.edit_message_text(text=f"Vous avez sélectionné {keys[-1]}. Choisissez une sous-catégorie:", reply_markup=keyboard)
        else:
            if "€" in keys[-1]:
                price = extract_price(dynamic_access(drugs_data, keys))
                add_to_cart(update.effective_user.id, keys[-1], price, update, context)
                display_cart(update, context)
            else:
                query.edit_message_text(text=f"Vous avez sélectionné {keys[-1]}. Aucune sous-catégorie disponible.")

def main():
    updater = Updater(token=constants["TELEGRAM_BOT_TOKEN"], use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_error_handler(handle_general_error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
