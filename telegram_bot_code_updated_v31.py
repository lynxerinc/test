import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les données du fichier drugs.json avec l'encodage correct
with open("data/drugs.json", "r", encoding="utf-8") as file:
    drugs_data = json.load(file)

user_carts = {}
user_message_ids = {}
id_to_data = {}
data_to_id = {}
current_id = 0

def get_username(update):
    user = update.effective_user
    return user.username if user and user.username else "no user"

def clear_cart(update, context):
    user_id = update.effective_user.id
    username = get_username(update)
    if user_id in user_carts:
        del user_carts[user_id]
    display_cart(update, context)
    logger.info(f"Utilisateur {user_id} ({username}) a vidé son panier.")

def add_to_cart(user_id, product, price, update, context):
    username = get_username(update)  # Ajout de cette ligne
    cart = user_carts.get(user_id, {})
    product_details = cart.get(product, {"price": price, "quantity": 0})
    product_details["quantity"] += 1
    cart[product] = product_details
    user_carts[user_id] = cart
    logger.info(f"Utilisateur {user_id} ({username}) a ajouté {product} ({price}€)")

def display_cart(update, context):
    user_id = update.effective_user.id
    username = get_username(update)
    cart = user_carts.get(user_id, {})
    
    total_price = 0
    cart_message = "🛒 Votre panier :\n---------------------\n"
    
    grouped_products = {}
    for product, details in cart.items():
        product_name, weight_price = product.split('-')[0].strip(), product.split('-')[1].strip()
        if product_name not in grouped_products:
            grouped_products[product_name] = []
        grouped_products[product_name].append((weight_price, details))

    for product_name, details_list in grouped_products.items():
        cart_message += f"🔹 {product_name}:\n"
        for detail in details_list:
            weight_price, product_detail = detail
            price = product_detail['price']
            quantity = product_detail['quantity']
            total_price += price * quantity
            cart_message += f"  - {weight_price} | Qté : {quantity} | Sous-total : {price * quantity}€\n"
    cart_message += "---------------------\nTotal : " + str(total_price) + "€"
    
    keyboard = [[InlineKeyboardButton("🗑️ Vider le panier", callback_data="clear_cart")]]
    markup = InlineKeyboardMarkup(keyboard)

    message_id = user_message_ids.get(user_id)
    if message_id:
        try:
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_id, text=cart_message, reply_markup=markup)
        except:
            message = context.bot.send_message(chat_id=update.effective_chat.id, text=cart_message, reply_markup=markup)
            user_message_ids[user_id] = message.message_id
    else:
        message = context.bot.send_message(chat_id=update.effective_chat.id, text=cart_message, reply_markup=markup)
        user_message_ids[user_id] = message.message_id

    logger.info(f"Utilisateur {user_id} ({username}) a affiché son panier.({total_price}€).")

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
    context.bot.send_message(chat_id=update.effective_chat.id, text='Choisissez une catégorie :', reply_markup=keyboard)

def dynamic_access(data, keys_sequence):
    for key in keys_sequence:
        data = data[key]
    return data

def button(update, context):
    query = update.callback_query

    if query.data == "clear_cart":
        clear_cart(update, context)
        return
    elif query.data == "cart":
        display_cart(update, context)
        return
    
    query.answer()

    button_id = int(query.data)
    if button_id == -1:  # The "Back" button
        keyboard = generate_keyboard(drugs_data)
        query.edit_message_text(text="Choisissez une catégorie:", reply_markup=keyboard)
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
            add_to_cart(update.effective_user.id, keys[-1], price, update, context)
            display_cart(update, context)
        else:
            query.edit_message_text(text=f"Vous avez sélectionné {keys[-1]}. Aucune sous-catégorie disponible.")

def main():
    updater = Updater(token='5938970819:AAGH21yb_8MEn3HieRRJ-4B1wNrDhIzLzHU', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()