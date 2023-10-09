import logging

# Configuration du logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_general_error(update, context, error_message="Une erreur inattendue s'est produite."):
    """
    Gestion des erreurs non spécifiques
    """
    logger.error(f"Erreur pour {update} : {context.error}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)

def handle_request_error(update, context, error):
    """
    Gestion des erreurs de requête HTTP
    """
    logger.error(f"Erreur de requête pour {update} : {error}")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Erreur lors de la réalisation de la requête. Veuillez réessayer.")

def handle_file_error(update, context, filename):
    """
    Gestion des erreurs liées aux fichiers
    """
    logger.error(f"Erreur de fichier pour {filename}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Erreur lors de l'ouverture du fichier {filename}.")
