from datetime import datetime
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Dictionnaires globaux et autres variables (vous pouvez les déplacer dans un module séparé si nécessaire)
user_carts = {}  # Supposons que ce dictionnaire est partagé ou importé
users = {}  # Supposons que ce dictionnaire est partagé ou importé

def generate_unique_id():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10))

def handle_checkout(update, context):
    info_message = """
    🛒 **Procédure de Checkout**
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
    admin_message += "===========================\n"
    admin_message += f"👤 Utilisateur: {username}\n"
    admin_message += f"🆔 ID du panier: {unique_cart_id}\n"
    admin_message += f"🕒 Heure: {current_time}\n"
    admin_message += f"💳 Moyen de paiement suggéré : {selected_payment_method}\n"  # Ajoutez cette ligne

    admin_message += "===========================\n\n"
    
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
    admin_message += "===========================\n"
    
    context.bot.send_message(chat_id=specific_user_chat_id, text=admin_message)
