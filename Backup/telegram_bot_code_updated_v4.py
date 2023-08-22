import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Load JSON data
with open("data/drugs.json", "r", encoding="utf-8") as drugs_file:
    drugs_data = json.load(drugs_file)

with open("data/hack.json", "r", encoding="utf-8") as hack_file:
    hack_data = json.load(hack_file)

# Function to create the keyboard buttons dynamically
def build_menu(data):
    buttons = []
    for key in data:
        buttons.append([InlineKeyboardButton(key, callback_data=key)])
    return buttons

# Start command
def start(update, context):
    keyboard = build_menu({"Drogues et Médicaments": {}, "Identité et Piratage": {}})
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose a category:', reply_markup=reply_markup)

# Button callback
def button(update, context):
    query = update.callback_query
    category = query.data
    if category == "Drogues et Médicaments":
        reply_markup = InlineKeyboardMarkup(build_menu(drugs_data[category]))
    elif category == "Identité et Piratage":
        reply_markup = InlineKeyboardMarkup(build_menu(hack_data[category]))
    else:
        # Handle sub-categories here
        pass
    query.edit_message_text(text=f"Available subcategories in {category}:", reply_markup=reply_markup)

# Main function
def main():
    updater = Updater(token='5938970819:AAGH21yb_8MEn3HieRRJ-4B1wNrDhIzLzHU', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
