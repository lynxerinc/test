import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Charger les données du fichier drugs.json avec l'encodage correct
with open("data/drugs.json", "r", encoding="utf-8") as file:
    drugs_data = json.load(file)


user_carts = {}

def add_to_cart(user_id, product, price):
    if user_id not in user_carts:
        user_carts[user_id] = {}
    if product in user_carts[user_id]:
        user_carts[user_id][product]['quantity'] += 1
    else:
        user_carts[user_id][product] = {'price': price, 'quantity': 1}
id_to_data = {}
data_to_id = {}
current_id = 0



def display_cart(update, context):
    user_id = update.effective_user.id
    cart = user_carts.get(user_id, {})
    if not cart:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Votre panier est vide.")
        return
    total_price = 0
    cart_message = "🛒 Votre panier :\n---------------------\n"
    for product, details in cart.items():
        price = details['price']
        quantity = details['quantity']
        total_price += price * quantity
        cart_message += f"🔹 {product}\n   Quantité : {quantity}\n   Sous-total : {price*quantity}€\n\n"
    cart_message += "---------------------\nTotal : " + str(total_price) + "€"
    context.bot.send_message(chat_id=update.effective_chat.id, text=cart_message)
def extract_price(price_str):
    return float(price_str.replace("€", "").replace(",", ".").strip())
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

def generate_keyboard(data, prefix="", back_data=None):
    keyboard = []
    for key in data.keys():
        current_key = prefix + key
        button_id = data_to_id[current_key]
        keyboard.append([InlineKeyboardButton(key, callback_data=str(button_id))])
    if back_data:
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=back_data), InlineKeyboardButton("🛒 CART", callback_data="cart")])
    return InlineKeyboardMarkup(keyboard)

def start(update, context):
    keyboard = generate_keyboard(drugs_data)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Choisissez une catégorie:', reply_markup=keyboard)



def dynamic_access(data, keys_sequence):
    for key in keys_sequence:
        data = data[key]
    return data

def button(update, context):
    query = update.callback_query
    if query.data == "cart":
        display_cart(update, context)
        return
    query.answer()
    
    button_id = int(query.data)
    if button_id == -1:  # The "Back" button
        keyboard = generate_keyboard(drugs_data)
        query.edit_message_text(text="Choisissez une catégorie:", reply_markup=keyboard)
        return
        start(update, context)
        return
    
    current_key = id_to_data[button_id]
    keys = current_key.split("/")
    
    next_data = drugs_data
    for key in keys:
        next_data = next_data[key]

    back_data = "-1" if len(keys) == 1 else str(data_to_id["/".join(keys[:-1])])
    if isinstance(next_data, dict):
        keyboard = generate_keyboard(next_data, current_key + "/", back_data)
        query.edit_message_text(text=f"Vous avez sélectionné {keys[-1]}. Choisissez une sous-catégorie:", reply_markup=keyboard)
    else:
        if "€" in keys[-1]:  # This is a product with a price
            price = extract_price(dynamic_access(drugs_data, keys))
            add_to_cart(update.effective_user.id, keys[-1], price)
            query.answer(f"Le produit {keys[-1]} a bien été ajouté au panier. Valeur totale : {sum([details['price'] * details['quantity'] for details in user_carts.get(update.effective_user.id, {}).values()])}€"), show_alert=True
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
