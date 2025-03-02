import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests
import sys
import time
import datetime

# Telegram bot token
TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WHATSAPP_URL = os.getenv('WHATSAPP_URL')

# Google Sheets credentials
GOOGLE_SHEETS_CREDS_FILE = 'google.json'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Connect to Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open('ניהול הוצאות הבית 2025').worksheet('נוכחי')
mapping_sheet = client.open('ניהול הוצאות הבית 2025').worksheet('mapping')

# Initialize the Telegram bot
bot = telebot.TeleBot(TOKEN)

# Define states
states = {}

# Define function to get data from Google Sheets when the bot starts
def get_data_from_sheets_on_start():
    print("start to check for empty categories...")
    global states
    # Reset states
    states = {'not_found_values': [], 'current_index': 0}
    # Get all values from column D
    column_d_values = sheet.col_values(4)[-15:] 
    #print(column_d_values)

    column_d = sheet.col_values(4)[1:] 
    current_day_in_month = datetime.date.today().day
    if current_day_in_month > 4:
        last_15_cells = [(row, value) for row, value in enumerate(column_d[-15:], start=len(column_d) - 13)]
    else:
        # Get only 5 cells
        last_15_cells = [(row, value) for row, value in enumerate(column_d[-5:], start=len(column_d) - 13)]
        
    for row, value in last_15_cells:
        first_cell_index = row
        break

    print("Index of the first cell in the last 15 values in column D:", first_cell_index)

    for index, value in enumerate(column_d_values, start=first_cell_index):
        corresponding_value_e = sheet.cell(index, 5).value
        #print(f"name: {value}, category: {corresponding_value_e}")
        if corresponding_value_e == "not found":
            states['not_found_values'].append(value)
    if states['not_found_values']:
        requests.get(WHATSAPP_URL)
        ask_user_for_input()
    else:
        print("No empty categories found.")
        bot.stop_polling()
        sys.exit()

# Define function to ask user for input for each "not found" value
def ask_user_for_input():
    global states
    value = states['not_found_values'][states['current_index']]
    print(f"Need to add category for the value '{value}'")
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
        sys.exit()

# Call the function to get data from Google Sheets when the bot starts
get_data_from_sheets_on_start()

# Start the bot
bot.polling()
