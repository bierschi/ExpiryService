import time
import logging
import random
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram.bot import Bot
from telegram.parsemode import ParseMode
from telegram.ext.dispatcher import run_async

RATE = range(1)
NOTIFY = range(1)


class ExpiryServiceTelegram:
    """ class ExpiryServiceTelegram to send messages to the Telegram chat

    USAGE:
            estelegram = ExpiryServiceTelegram(token='')
            estelegram.new_msg()

    """
    def __init__(self, token, chatid):
        self.logger = logging.getLogger('ExpiryService')
        self.logger.info('Create class ExpiryServiceTelegram')

        self.token = token
        self.updater = Updater(token=self.token, use_context=True)
        self.dp = self.updater.dispatcher
        self.bot = Bot(token=self.token)

        # handler to get the commands description
        self.add_handler(command="help", handler=self.help)

        # conversation handler for the notifications
        self.notify_conv_handler = ConversationHandler(entry_points=[CommandHandler('notify', self.notification)],
                                                       states={NOTIFY: [MessageHandler(Filters.text, self.notify_on_off)]},
                                                       fallbacks=[CommandHandler('stop', self.stop)])

        self.dp.add_handler(self.notify_conv_handler)

        # event handler
        self.notify_event_handler = None

    def run(self, blocking=False):
        """ runs the telegram updater

        """
        self.updater.start_polling()
        if blocking:
            self.updater.idle()

    def add_handler(self, command, handler):
        """ add a handler function to the dispatcher

        :param command: command msg
        :param handler: handler function to execute
        """
        self.dp.add_handler(handler=CommandHandler(command=command, callback=handler))

    @run_async
    def help(self, update, context):
        """ get the description of ExpriyService

        :param bot: bot
        :param update: update

        :return: help description
        """
        chat_id = update.message.chat_id
        user = update.message.from_user
        self.logger.info("User {} with userid: {} requests the help description".format(user.username, user.id))

        help_msg = "*Welcome to ExpiryService*\n\nAvailable commands:\n" \
                   "/: \n" \
                   "/: \n" \
                    "/: \n" \
                   "/help: Usage of ExpiryService"

        context.bot.send_message(chat_id=chat_id, text=help_msg, parse_mode=ParseMode.MARKDOWN)

    def stop(self, update, context):
        """ stops the  conversation

        :param update: update
        :param context: context

        :return: reply text
        """
        update.message.reply_text('Bye! I hope we can talk again some day.')

        return ConversationHandler.END
