
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# Configuration des logs
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Liste des IDs d'admin pour la liste blanche
admin_ids = ["1709873116"]  # Remplacez par vos IDs d'admin

# Drapeau pour vérifier si l'admin est vérifié
is_verified_admin = False

# Espace réservé pour la fonctionnalité admin
def admin_functionality(update: Update, context: CallbackContext) -> None:
    print("Admin functionality called")  # Debugging print
    update.message.reply_text("Fonctionnalité admin en attente.")
    logger.info(f"Fonctionnalité admin accédée par {update.effective_user.id}")

# Fonction pour vérifier l'admin
def verify_admin(update: Update, context: CallbackContext) -> None:
    print("Verify admin called")  # Debugging print
    global is_verified_admin
    user_id = str(update.effective_user.id)
    if user_id in admin_ids:
        is_verified_admin = True
        update.message.reply_text("Vous êtes vérifié en tant qu'admin.")
        logger.info(f"Admin vérifié : {user_id}")
    else:
        update.message.reply_text("Vous n'êtes pas autorisé à utiliser ce bot.")
        logger.warning(f"Tentative d'accès non autorisée par {user_id}")

# Fonction de démarrage aussi abstraite que possible
def start(update: Update, context: CallbackContext) -> None:
    global is_verified_admin
    if not is_verified_admin:
        update.message.reply_text("Vous devez d'abord vous vérifier en tant qu'admin. Utilisez /verify.")
        logger.warning(f"Vérification d'admin requise pour {update.effective_user.id}")
        return
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='1')],
        [InlineKeyboardButton("Option 2", callback_data='2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choisissez une option :", reply_markup=reply_markup)
    logger.info(f"Commande de démarrage accédée par un admin vérifié : {update.effective_user.id}")

def main() -> None:
    print("Bot is starting")  # Debugging print
    # Initialisation de l'Updater
    updater = Updater("6140284584:AAF8gviWzKMkHEn5TktrVMral7PPMW7uxXk")
    
    # Récupération du dispatcher pour enregistrer les gestionnaires
    dispatcher = updater.dispatcher

    # Enregistrement des gestionnaires de commande
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("verify", verify_admin))
    dispatcher.add_handler(CommandHandler("admin", admin_functionality))
    
    logger.info("Bot started")
    
    # Démarrage du Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()