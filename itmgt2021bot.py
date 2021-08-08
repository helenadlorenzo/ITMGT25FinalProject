import logging
import requests
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('''
    Welcome to MoneyX! Here is a full list of commands:\n

See a full list of commands.\t
Type "/help"\n

Convert one amount to any number/combination of desired currencies.\t
Type "/convert [CURRENCY] [AMOUNT] to [DESIRED CURRENCY 1] [DESIRED CURRENCY 2]..."\t
(ex. /convert php 100.50 to usd eur hkd).\n

Add and/or subtract values in different currencies and get the output in one currency.\t
Type "/calculate [CURRENCY1] [AMOUNT1] + [CURRENCY2] [AMOUNT2] - [CURRENCY3] [AMOUNT3] ... to [DESIRED CURRENCY]\t
(ex. /calculate php 500 - hkd 430.2 to usd)\n

See a graph of the currency rate trend between two currencies from the last 30 days.\t
Type "/history [CURRENCY 1] to [CURRENCY2]" (ex. /history php to usd)
    ''')

def convert(update: Update, context: CallbackContext) -> None:
    r = requests.get('http://api.exchangeratesapi.io/v1/latest?access_key=9a223be759130d6d46862c6665f63926')

    try:
        currency1_name = context.args[0].upper()
        currency1_rate = r.json()['rates'][currency1_name]
        currency1_value = float(context.args[1])

        currency2_name = context.args[3:]
        result_formatted = 'as of ' + r.json()['date']
        for i in range(len(currency2_name)):
            currency2_name_indiv = currency2_name[i].upper()
            currency2_rate = r.json()['rates'][currency2_name_indiv]
            currency2_value = (currency1_value/currency1_rate) * currency2_rate

            result_formatted += '\n' + currency1_name + ' ' + str(currency1_value) + ' = ' + currency2_name_indiv + ' ' + str(currency2_value)
        
        update.message.reply_text(result_formatted)
    except:
        update.message.reply_text('Error. Please try again. Enter /help to see a list of commands.')

def calculate(update: Update, context: CallbackContext) -> None:
    r = requests.get('http://api.exchangeratesapi.io/v1/latest?access_key=9a223be759130d6d46862c6665f63926')

    try:
        # first conversion
        currency1_name = context.args[0].upper()
        currency1_rate = r.json()['rates'][currency1_name]
        currency1_value = float(context.args[1])

        currency2_name = context.args[-1].upper()
        currency2_rate = r.json()['rates'][currency2_name]
        currency2_value = (currency1_value/currency1_rate) * currency2_rate
        result_value = currency2_value
        result_formatted = 'as of ' + r.json()['date']
        result_formatted += '\n' + currency1_name + ' ' + str(currency1_value)

        # second conversion
        try:
            currency_other = context.args[2:-2]
            currency_other_num = int(len(currency_other) / 3)
            for i in range(currency_other_num):
                currency3_name = context.args[1 + (i * 3) + 2].upper()
                currency3_rate = r.json()['rates'][currency3_name]
                currency3_operator = context.args[1 + (i * 3) + 1]
                currency3_absvalue = float(context.args[1 + (i * 3) + 3])
                currency3_value = float(currency3_operator + str(currency3_absvalue))

                currency4_name = context.args[-1].upper()
                currency4_rate = r.json()['rates'][currency4_name]
                currency4_value = (currency3_value/currency3_rate) * currency4_rate

                result_value += currency4_value
                result_formatted += ' ' + currency3_operator + ' ' + currency3_name + ' ' + str(currency3_absvalue)

            result_formatted += ' = ' + currency4_name + ' ' + str(result_value)

        except:
            result_formatted += ' = ' + currency2_name + ' ' + str(currency2_value)
        
        update.message.reply_text(result_formatted)
    except:
        update.message.reply_text('Error. Please try again. Enter /help to see a list of commands.')

def history(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    bot = TelegramBot("1930727729:AAEEsKKfPyVlW-Ea2UNGBTzkugMXLeBIB3E", chat_id)

    try:
        #ex. USD to PHP
        currency1_name = context.args[0].upper()
        currency2_name = context.args[2].upper()
        base_url="https://www.exchange-rates.org/history/"
        extension=f"{currency2_name}/{currency1_name}/T"
        url=f"{base_url}{extension}"
    
        dfs = pd.read_html(url)
        
        date=dfs[0][0][0:30]

        price=dfs[0][2][0:30].str.rstrip(currency2_name).astype('float')
        fig=plt.figure(figsize=(20, 10), dpi=80)      
        plt.plot(date,price,"b",linewidth=2.50)
        plt.gca().invert_xaxis()
        plt.xlabel("Day",fontsize=16)
        plt.ylabel("Price",fontsize=16)
        plt.xticks(rotation=45)
        plt.title(f"Exchange rate of {currency2_name} per {currency1_name} in the past 30 days")

        update.message.reply_text('This may take a while. Please standby.')
        bot.send_plot(plt)
        
    except:
        update.message.reply_text('Error. Please try again. Enter /help to see a list of commands.')

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('''
    Here is a full list of commands:\n

Convert one amount to any number/combination of desired currencies.\t
Type "/convert [CURRENCY] [AMOUNT] to [DESIRED CURRENCY 1] [DESIRED CURRENCY 2]..."\t
(ex. /convert php 100.50 to usd eur hkd).\n

Add and/or subtract values in different currencies and get the output in one currency.\t
Type "/calculate [CURRENCY1] [AMOUNT1] + [CURRENCY2] [AMOUNT2] - [CURRENCY3] [AMOUNT3] ... to [DESIRED CURRENCY]\t
(ex. /calculate php 500 - hkd 430.2 to usd)\n

See a graph of the currency rate trend between two currencies from the last 30 days.\t
Type "/history [CURRENCY 1] to [CURRENCY2]" (ex. /history php to usd)
    ''')

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def main() -> None:
    updater = Updater("1930727729:AAEEsKKfPyVlW-Ea2UNGBTzkugMXLeBIB3E")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("convert", convert))
    dispatcher.add_handler(CommandHandler("calculate", calculate))
    dispatcher.add_handler(CommandHandler("history", history))

    updater.start_polling()

    updater.idle()




if __name__ == '__main__':
    main()
