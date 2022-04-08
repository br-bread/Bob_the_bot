import logging
from telegram.ext import Updater, MessageHandler, Filters

logger = logging.getLogger(__name__)

TOKEN = '5235508319:AAH_BNimCWuKBi1K2h71zey92tq1RMMmreg'

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()