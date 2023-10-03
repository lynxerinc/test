import logging
import json
import secrets
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime

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
users = {}

# Sauvegarder les données utilisateur dans un fichier
def save_users_to_file(users, filename="users.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False)

# Charger les données utilisateur au démarrage
def load_users_from_file(filename="users.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

users = load_users_from_file()

def read_bot_status(filename="data/bot_status.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("is_open", True)
    except FileNotFoundError:
        return True

def get_username(update):
    user = update.effective_user
    return user.username if user and user.username else "no user"

def update_user_info(user_id, action_type, update, context=None):
    user_info = users.get(user_id, {"username": get_username(update), "actions": []})
    action = {"type": action_type, "details": context}
    user_info["actions"].append(action)
    users[user_id] = user_info
    save_users_to_file(users)

def clear_cart(update, context):
    user_id = update.effective_user.id
    username = get_username(update)
    if user_id in user_carts:
        del user_carts[user_id]
    display_cart(update, context)
    logger.info(f"Utilisateur {user_id} (user {username}) a vidé son panier.")
    update_user_info(user_id, "cleared_cart", update)

def add_to_cart(user_id, product, price, update, context):
    cart = user_carts.get(user_id, {})
    product_details = cart.get(product, {"price": price, "quantity": 0})
    product_details["quantity"] += 1
    cart[product] = product_details
    user_carts[user_id] = cart
    username = get_username(update)
    logger.info(f"Utilisateur {user_id} (user {username}) a ajouté {product} (prix: {price}€) à son panier.")
    update_user_info(user_id, "added_to_cart", update, {"product": product, "price": price})

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

# Nouvelle fonction pour supprimer des produits spécifiques
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
    user_id = update.effective_user.id
    username = get_username(update)

    is_open = read_bot_status()
    if not is_open:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="🚧 *Service temporairement indisponible* 🚧\n\n"
                                      "Chers utilisateurs,\n\n"
                                      "Nous vous informons que notre service est actuellement indisponible pour l'une des raisons suivantes :\n"
                                      "1️⃣ *Maintenance des serveurs* : Nos équipes travaillent à l'amélioration de notre infrastructure.\n"
                                      "2️⃣ *Trop grand nombre de commandes* : Nous avons atteint notre capacité maximale.\n"
                                      "3️⃣ *Mise à jour du système* : Nous mettons à jour notre plateforme.\n\n"
                                      "Nous prévoyons de rétablir le service dans les prochaines *24* heures.\n"
                                      "Pour toute question, n'hésitez pas à nous contacter.\n\n"
                                      "Merci de votre compréhension.",
                                 parse_mode='Markdown')
        return    

    # Vérifier si l'utilisateur existe déjà
    if user_id not in users:
        users[user_id] = {"username": username, "actions": []}
        save_users_to_file(users) # Sauvegarder les données utilisateur dans le fichier

        # Message de bienvenue pour les nouveaux utilisateurs
        welcome_message = f"Bienvenue, {username}!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

    keyboard = generate_keyboard(drugs_data)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Choisissez une catégorie :', reply_markup=keyboard)

def dynamic_access(data, keys_sequence):
    for key in keys_sequence:
        data = data[key]
    return data

def generate_unique_id():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10))

def button(update, context):
    query = update.callback_query
    
    # Pour effacer le panier
    if query.data == "clear_cart":
        clear_cart(update, context)
        return
    
    # Pour afficher le panier
    elif query.data == "cart":
        display_cart(update, context)
        return
    
    # Pour supprimer un produit spécifique du panier
    elif query.data == "delete_products":
        delete_specific_product(update, context)
        return

    elif query.data == "checkout":
        info_message = """
        🛒 **Procédure de Checkout - Étape par Étape** 🛒
        ---------------------------------------
        
        🌟 **Étape 1 : Sélection du Mode de Paiement**
        À cette étape, vous aurez le choix entre plusieurs options de paiement : Bitcoin, Monero, Solana, VRM, et paiement en espèces pour les retraits sur place. Chaque option a ses propres avantages et inconvénients. Assurez-vous de choisir celle qui vous convient le mieux, car cela déterminera le processus que vous devrez suivre par la suite.
        
        🌟 **Étape 2 : Fourniture du Fichier PGP**
        Avant de procéder au paiement, vous devrez nous fournir un fichier PGP contenant les détails de votre livraison. Ce fichier sera utilisé pour chiffrer toutes les communications ultérieures concernant votre commande.
        
        🌟 **Étape 3 : Vérification des Informations**
        Une fois le fichier PGP reçu, nous procéderons à la vérification des informations qu'il contient. Ce processus peut prendre un peu de temps, mais il est essentiel pour garantir la confidentialité et la sécurité de votre commande.
        
        🌟 **Étape 4 : Détails du Paiement**
        Après avoir vérifié vos informations, nous vous enverrons les détails pour effectuer le paiement. Ces informations seront chiffrées avec le fichier PGP que vous avez fourni pour garantir leur sécurité.
        
        🌟 **Étape 5 : Confirmation et Livraison**
        Après réception et vérification du paiement, votre commande sera préparée et expédiée. Vous recevrez une confirmation chiffrée et des informations sur le suivi de la livraison.
        
        📌 **Note Importante**
        Pour garantir une expérience d'achat sécurisée, assurez-vous de suivre ces étapes attentivement. En cas de problème ou de question, n'hésitez pas à nous contacter.
        
        Merci de faire confiance à notre service ! Nous nous réjouissons de vous offrir une expérience d'achat sécurisée et satisfaisante.
        """
        context.bot.send_message(chat_id=update.effective_chat.id, text=info_message)
        
        keyboard = [
            [InlineKeyboardButton("Bitcoin", callback_data="payment_bitcoin")],
            [InlineKeyboardButton("Monero", callback_data="payment_monero")],
            [InlineKeyboardButton("Solana", callback_data="payment_solana")],
            [InlineKeyboardButton("VRM", callback_data="payment_vrm")],
            [InlineKeyboardButton("Espèce (Retraits sur place uniquement)", callback_data="payment_cash")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Choisissez votre moyen de paiement:", reply_markup=markup)
    
        username = get_username(update)
        specific_user_chat_id = 1709873116  # Remplacez cela par l'identifiant de chat de l'utilisateur spécifique
        cart = user_carts.get(update.effective_user.id, {})
        
        # Générez l'identifiant unique
        unique_cart_id = generate_unique_id()
        
        # Obtenez l'heure actuelle
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Liste des moyens de paiement disponibles
        payment_methods = ['Bitcoin', 'Monero', 'Solana', 'VRM', 'Espèce']
        
        # Sélectionnez un moyen de paiement aléatoire
        selected_payment_method = random.choice(payment_methods)
        
        # Initialisez le message et le total
        admin_message = "🛒🛒🛒 NOUVELLE COMMANDE 🛒🛒🛒\n"
        admin_message += "===================================\n"
        admin_message += f"👤 Utilisateur: {username}\n"
        admin_message += f"🆔 ID du panier: {unique_cart_id}\n"
        admin_message += f"🕒 Heure: {current_time}\n"
        admin_message += f"💳 Moyen de paiement suggéré : {selected_payment_method}\n"  # Ajoutez cette ligne

        admin_message += "===============================\n\n"
        
        admin_message += "📦 Détails de la Commande 📦\n"
        admin_message += "-----------------------------------\n"
        
        total_price = 0
        cart = user_carts.get(update.effective_user.id, {})
        
        for product, details in cart.items():
            quantity = details["quantity"]
            price = details["price"]
            total_price += price * quantity
            admin_message += f"🔹 {product}\n"
            admin_message += f"    - Quantité: {quantity}\n"
            admin_message += f"    - Prix unitaire: {price}€\n"
            admin_message += f"    - Sous-total: {price * quantity}€\n"
        
        admin_message += "-----------------------------------\n"
        admin_message += f"💰 TOTAL : {total_price}€\n"
        admin_message += "===============================\n"
        
        context.bot.send_message(chat_id=specific_user_chat_id, text=admin_message)
        
    elif query.data.startswith("payment_"):
        payment_method = query.data.split("_")[1]
        payment_info = "Voici les détails pour effectuer le paiement..."  # Valeur par défaut
    
        if payment_method == "bitcoin":
            payment_info = "Option Bitcoin confirmée. Veuillez suivre les étapes suivantes :\n" \
                           "1. Fournissez-nous votre fichier PGP contenant les détails de votre livraison.\n" \
                           "2. Une fois les informations vérifiées, nous vous enverrons l'adresse Bitcoin pour effectuer le paiement."
        
        elif payment_method == "monero":
            payment_info = "Option Monero confirmée. Veuillez suivre les étapes suivantes :\n" \
                           "1. Fournissez-nous votre fichier PGP contenant les détails de votre livraison.\n" \
                           "2. Une fois les informations vérifiées, nous vous enverrons l'adresse Monero pour effectuer le paiement."
        
        elif payment_method == "solana":
            payment_info = "Option Solana confirmée. Veuillez suivre les étapes suivantes :\n" \
                           "1. Fournissez-nous votre fichier PGP contenant les détails de votre livraison.\n" \
                           "2. Une fois les informations vérifiées, nous vous enverrons l'adresse Solana pour effectuer le paiement."
        
        elif payment_method == "vrm":
            payment_info = "Option VRM confirmée. Veuillez suivre les étapes suivantes :\n" \
                           "1. Fournissez-nous votre fichier PGP contenant les détails de votre livraison.\n" \
                           "2. Une fois les informations vérifiées, nous vous enverrons l'adresse VRM pour effectuer le paiement."
        
        elif payment_method == "cash":
            payment_info = "Option Espèce confirmée (Retraits sur place uniquement). Veuillez suivre les étapes suivantes :\n" \
                           "1. Fournissez-nous votre fichier PGP contenant les détails de votre livraison.\n" \
                           "2. Une fois les informations vérifiées, vous pourrez vous rendre au point de retrait pour effectuer le paiement en espèces."

    
        context.bot.send_message(chat_id=update.effective_chat.id, text=payment_info)

    
        # Demande du fichier PGP
        keyboard = [[InlineKeyboardButton("🔐 Envoyer le fichier PGP", callback_data="send_pgp")]]
        markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Veuillez envoyer votre fichier PGP pour les détails de livraison.", reply_markup=markup)

    elif query.data == "send_pgp":
        error_message = "Le format standard pour l'envoi de fichiers PGP n'est pas respecté. Veuillez suivre les instructions fournies."
        context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)    
    
    # Pour gérer la suppression d'un produit spécifique
    try:
        button_id = int(query.data)
    except ValueError:
        if query.data.startswith("delete_product:"):
            product_to_delete = query.data.split(":")[1]
            if product_to_delete.startswith("{") and product_to_delete.endswith("}"):
                product_to_delete = product_to_delete[1:-1]
            delete_product(update, context, product_to_delete)
            return
        else:
            logger.error(f"Invalid button data: {query.data}")
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