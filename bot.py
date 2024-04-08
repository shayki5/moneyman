import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Telegram bot token
TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Google Sheets credentials
GOOGLE_SHEETS_CREDS_FILE = 'google.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Connect to Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open('ניהול הוצאות הבית 2024').worksheet('נוכחי')
mapping_sheet = client.open('ניהול הוצאות הבית 2024').worksheet('mapping')

# Initialize the Telegram bot
bot = telebot.TeleBot(TOKEN)

# Define states
states = {}

# Define function to get data from Google Sheets when the bot starts
def get_data_from_sheets_on_start():
    global states
    # Reset states
    states = {'not_found_values': [], 'current_index': 0}
    # Get all values from column D
    column_d_values = sheet.col_values(4)  # Get values from column D (index 4)
    for index, value in enumerate(column_d_values, start=1):
        corresponding_value_e = sheet.cell(index, 5).value  # Get corresponding value from column E (index 5)
        if corresponding_value_e == "not found":
            states['not_found_values'].append(value)
    if states['not_found_values']:
        ask_user_for_input()
    else:
        print("no not-found cells!")
        bot.stop_polling()

# Define function to ask user for input for each "not found" value
def ask_user_for_input():
    global states
    value = states['not_found_values'][states['current_index']]
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"For the value '{value}' in column D, please provide your input:")
    states['current_value'] = value
    states['state'] = 'waiting_for_input'

# Define function to process user input for each value
@bot.message_handler(func=lambda message: states.get('state') == 'waiting_for_input')
def process_input_for_value(message):
    global states
    input_text = message.text
    value = states['current_value']
    bot.reply_to(message, f"Input '{input_text}' received for value '{value}' in column D. Updating mapping sheet...")
    mapping_sheet.append_row([value, input_text])
    states['current_index'] += 1
    if states['current_index'] < len(states['not_found_values']):
        ask_user_for_input()
    else:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="All values processed.")
        states = {}
        bot.stop_polling()

# Call the function to get data from Google Sheets when the bot starts
get_data_from_sheets_on_start()

# Start the bot
bot.polling()