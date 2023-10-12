from telegram.ext import Updater, CommandHandler

# Fonction pour gérer la commande 'start'
def start(update, context):
    update.message.reply_text('Salut')

# Initialisation du bot
updater = Updater(token='6140284584:AAF8gviWzKMkHEn5TktrVMral7PPMW7uxXk', use_context=True)

# Gestionnaire de commandes
dispatcher = updater.dispatcher

# Ajout d'un gestionnaire pour la commande 'start'
dispatcher.add_handler(CommandHandler('start', start))

# Démarrer le bot
updater.start_polling()
