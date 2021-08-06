import logging
import requests
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! Please type "/convert \[AMOUNT\] \[CURRENCY\] to \[DESIRED CURRENCY\]" \(ex\. \/convert 100 PHP to USD\)',
        reply_markup=ForceReply(selective=True),
    )

def convert(update: Update, context: CallbackContext) -> None:
    print(context.args)
    r = requests.get('http://api.exchangeratesapi.io/v1/latest?access_key=9a223be759130d6d46862c6665f63926')

    currency1_name = context.args[1].upper()
    currency2_name = context.args[3].upper()

    currency1_rate = r.json()['rates'][context.args[1].upper()]
    currency2_rate = r.json()['rates'][context.args[3].upper()]

    currency1_value = float(context.args[0])
    currency2_value = (currency1_value/currency1_rate) * currency2_rate
    result_formatted = currency1_name + ' ' + str(currency1_value) + ' = ' + currency2_name + ' ' + str(currency2_value)
    update.message.reply_text(result_formatted)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Please type "convert [AMOUNT] [CURRENCY] to [DESIRED CURRENCY]" (ex. /convert 100 PHP to USD)')

def echo(update: Update, context: CallbackContext) -> None:
    #"""Echo the user message."""
    update.message.reply_text(update.message.text)

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1930727729:AAEEsKKfPyVlW-Ea2UNGBTzkugMXLeBIB3E")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("convert", convert))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()