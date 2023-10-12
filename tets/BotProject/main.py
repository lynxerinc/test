import logging
from telegram.ext import CommandHandler, CallbackContext, Updater, MessageHandler, Filters
from utils.ban_manager import is_banned

# Configuration du logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='logging/main.log', level=logging.INFO, format=log_format)

# Ajoute un gestionnaire de log pour la sortie console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(console_handler)

def start(update, context):
    user_id = update.effective_chat.id
    is_banned_status, reason = is_banned(update, context)
    if is_banned_status:
        logging.warning(f"Utilisateur {user_id} est banni.")
        context.bot.send_message(chat_id=user_id, text=f"Vous avez été banni pour la raison suivante : {reason}")
        return
    logging.info(f"Utilisateur {user_id} autorisé.")
    context.bot.send_message(chat_id=user_id, text="Salut")

def main():
    try:
        updater = Updater(token='6140284584:AAF8gviWzKMkHEn5TktrVMral7PPMW7uxXk', use_context=True)
        dp = updater.dispatcher
        start_handler = CommandHandler('start', start)
        dp.add_handler(start_handler)
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logging.error(f"Erreur : {e}")

if __name__ == '__main__':
    main()
