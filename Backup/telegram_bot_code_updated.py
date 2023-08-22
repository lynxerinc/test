
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from collections import defaultdict
import logging

# Function to process the content of the file and organize it by categories and subcategories
def process_file(file_path):
    organized_content = defaultdict(lambda: defaultdict(list))
    current_category = None
    current_subcategory = None
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("## "):  # Category
                current_category = line[3:]
                current_subcategory = None
            elif line.startswith("### "):  # Subcategory
                current_subcategory = line[4:]
            elif line.startswith("- "):  # Item
                item = line[2:]
                if current_subcategory:
                    organized_content[current_category][current_subcategory].append(item)
                else:
                    organized_content[current_category][""].append(item)
    return organized_content

# Loading categories, subcategories, and products from the file
file_path = 'snapplan.md'
categories = process_file(file_path)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle the start command
def start(update: Update, _: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("💊listings", callback_data='listings')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to the Snap plan bot! Click on the listings to see available categories.', reply_markup=reply_markup)

# Function to handle listing callback
def listings_callback(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton(category, callback_data=f'category:{category}')] for category in categories.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Available categories:", reply_markup=reply_markup)

# Function to handle category callback
def category_callback(update: Update, category: str, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    subcategories = categories[category].keys()
    if not subcategories:
        # If there are no subcategories, display the products directly
        keyboard = [[InlineKeyboardButton(product, callback_data='product')] for product in categories[category][""]]
    else:
        keyboard = [[InlineKeyboardButton(subcategory, callback_data=f'subcategory:{category}:{subcategory}')] for subcategory in subcategories]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Available subcategories in {category}:", reply_markup=reply_markup)

# Function to handle subcategory callback
def subcategory_callback(update: Update, category: str, subcategory: str, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton(product, callback_data='product')] for product in categories[category][subcategory]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Available products in {subcategory}:", reply_markup=reply_markup)

# Function to handle callback queries
def button(update: Update, context: CallbackContext) -> None:
    query_data = update.callback_query.data
    if query_data == 'listings':
        listings_callback(update, context)
    elif query_data.startswith('category:'):
        _, category = query_data.split(':')
        category_callback(update, category, context)
    elif query_data.startswith('subcategory:'):
        _, category, subcategory = query_data.split(':')
        subcategory_callback(update, category, subcategory, context)

# Main function to run the bot
def main() -> None:
    updater = Updater("5938970819:AAGH21yb_8MEn3HieRRJ-4B1wNrDhIzLzHU") # Insert your API Token here
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
