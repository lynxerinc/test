import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionnaires globaux (vous pouvez les déplacer dans un module séparé si nécessaire)
user_carts = {}
user_message_ids = {}
current_id = 0
id_to_data = {}
data_to_id = {}

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

def get_username(update):
    user = update.effective_user
    return user.username if user and user.username else "no user"

def clear_cart(update, context):
    user_id = update.effective_user.id
    username = get_username(update)
    if user_id in user_carts:
        del user_carts[user_id]
    display_cart(update, context)
    logger.info(f"Utilisateur {user_id} (user {username}) a vidé son panier.")

def add_to_cart(user_id, product, price, update, context):
    cart = user_carts.get(user_id, {})
    product_details = cart.get(product, {"price": price, "quantity": 0})
    product_details["quantity"] += 1
    cart[product] = product_details
    user_carts[user_id] = cart
    username = get_username(update)
    logger.info(f"Utilisateur {user_id} (user {username}) a ajouté {product} (prix: {price}€) à son panier.")

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
    
    keyboard = [
        [
            InlineKeyboardButton("🗑️ Vider tout le panier", callback_data="clear_cart"),
            InlineKeyboardButton("🗑️ Supprimer des produits", callback_data="delete_products")
        ]
    ]
    if cart:  # Si le panier n'est pas vide
        keyboard.append([InlineKeyboardButton("🛒 Checkout", callback_data="checkout")])        
    
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

def delete_specific_product(update, context):
    user_id = update.effective_user.id
    cart = user_carts.get(user_id, {})

    if not cart:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Votre panier est vide.")
        return

    keyboard = []
    for product in cart.keys():
        keyboard.append([InlineKeyboardButton(f"❌ {product}", callback_data=f"delete_product:{product}")])

    keyboard.append([InlineKeyboardButton("🔙 Revenir au panier", callback_data="cart"), InlineKeyboardButton("🗑️ Vider tout le panier", callback_data="clear_cart")])

    markup = InlineKeyboardMarkup(keyboard)

    message_id = user_message_ids.get(user_id)
    context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id, message_id=message_id, reply_markup=markup)

def delete_product(update, context, product_to_delete):
    user_id = update.effective_user.id
    cart = user_carts.get(user_id, {})

    if product_to_delete in cart:
        del cart[product_to_delete]

    display_cart(update, context)
