import json
import requests
import time
import random
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Dictionnaires globaux et autres variables (vous pouvez les déplacer dans un module séparé si nécessaire)
user_carts = {}  # Supposons que ce dictionnaire est partagé ou importé
user_message_ids = {}  # Supposons que ce dictionnaire est partagé ou importé
data_to_id = {}
counter = 0

def populate_data_to_id(data, prefix=""):
    global counter
    for key in data.keys():
        counter += 1
        data_to_id[prefix + key] = counter
        if isinstance(data[key], dict):
            populate_data_to_id(data[key], prefix=f"{key}>")

# Charger le JSON depuis un fichier ou une autre source
your_json_data = {
	"Gaz à inhaler": {
		"Protoxyde d'Azote": {
			"Protoxyde D'azote 666G - Creamy Deluxe": {
				"6 bonbonnes - 120€": "120",
				"12 bonbonnes - 240€": "240",
				"18 bonbonnes - 360€": "360"
			},
			"Protoxyde d'azote 580G - Saveur CD": {
				" Fraise": {
					"6 bonbonnes Fraise - 138€": "138"
				},
				"Sucre": {
					"6 bonbonnes Sucre - 138€": "138"
				},
				"Pêche": {
					"6 bonbonnes Pêche - 138€": "138"
				}
			}
		}
	}
}

populate_data_to_id(your_json_data)


def get_username(update):
    user = update.effective_user
    return user.username if user and user.username else "no user"

def read_bot_status():
    # Lire l'URL à partir du fichier JSON
    with open("constants.json", "r") as f:
        config = json.load(f)
    url = config.get("BOT_STATUS_URL")  # Assurez-vous que cela correspond à la clé dans le fichier JSON
    
    # Ajouter un paramètre aléatoire pour contourner le cache
    random_timestamp = str(time.time()) + str(random.randint(1, 1000))
    url = f"{url}?rand={random_timestamp}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("is_open", True)
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier bot_status.json : {e}")
    return True

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

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_keyboard(data, prefix=""):
    keyboard = []
    for key in data.keys():
        key_id = data_to_id.get(prefix + key, None)
        if key_id is not None:
            keyboard.append([InlineKeyboardButton(key, callback_data=str(key_id))])
    return InlineKeyboardMarkup(keyboard)



def dynamic_access(data, keys_sequence):
    for key in keys_sequence:
        data = data[key]
    return data

def display_cart(update, context):
    user_id = update.effective_user.id
    username = get_username(update)
    cart = user_carts.get(user_id, {})
    
    total_price = 0
    cart_message = "🛒 Votre panier :\\n---------------------\\n"
    
    grouped_products = {}
    for product, details in cart.items():
        product_name, weight_price = product.split('-')[0].strip(), product.split('-')[1].strip()
        if product_name not in grouped_products:
            grouped_products[product_name] = []
        grouped_products[product_name].append((weight_price, details))

    for product_name, details_list in grouped_products.items():
        cart_message += f"🔹 {product_name}:\\n"
        for detail in details_list:
            weight_price, product_detail = detail
            price = product_detail['price']
            quantity = product_detail['quantity']
            total_price += price * quantity
            cart_message += f"  - {weight_price} | Qté : {quantity} | Sous-total : {price * quantity}€\\n"
    cart_message += "---------------------\\nTotal : " + str(total_price) + "€"
    
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

def extract_price(price_str):
    return float(price_str.replace("€", "").replace(",", ".").strip())
