from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def handle_payment_method(update, context, payment_method):
    payment_info = "Voici les détails pour effectuer le paiement..."  # Valeur par défaut

    if payment_method == "bitcoin":
        payment_info = "Option Bitcoin confirmée. Veuillez suivre les étapes suivantes :\n" \
                       "1. Fournissez-nous votre fichier PGP contenant les détails de votre livraison.\n" \
                       "2. Une fois les informations vérifiées, nous vous enverrons l'adresse Bitcoin pour effectuer le paiement."
        
    elif payment_method == "monero":
        payment_info = "Option Monero confirmée. Veuillez suivre les étapes suivantes ..."
        # Ajoutez les instructions pour Monero ici
    
    elif payment_method == "solana":
        payment_info = "Option Solana confirmée. Veuillez suivre les étapes suivantes ..."
        # Ajoutez les instructions pour Solana ici

    elif payment_method == "vrm":
        payment_info = "Option VRM confirmée. Veuillez suivre les étapes suivantes ..."
        # Ajoutez les instructions pour VRM ici
    
    elif payment_method == "cash":
        payment_info = "Option Espèce confirmée. Cette option est uniquement disponible pour les retraits sur place."
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=payment_info)
    
    # Demande du fichier PGP
    keyboard = [[InlineKeyboardButton("🔐 Envoyer le fichier PGP", callback_data="send_pgp")]]
    markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Veuillez envoyer votre fichier PGP pour les détails de livraison.", reply_markup=markup)
