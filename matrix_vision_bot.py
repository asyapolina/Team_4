from datetime import datetime
import functools
import logging
import os

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

from matrix_vision.configs import Config
from matrix_vision.matrix_vision import MatrixVision

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

log = logging.getLogger()
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Hi, {update.effective_user.first_name}!')
    update.message.reply_text('Send /help to know about usage.')


def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Hi! I am bot for creating animation in matrix style from image.')
    update.message.reply_text('To start just send me an image.')


def reply_to_text(update: Update, context: CallbackContext):
    """Send some help to user."""
    update.message.reply_text("Image is expected!")


def reply_to_image(update: Update, context: CallbackContext, config: Config):
    """Send animated photo in matrix vision style to user."""
    img =  update.message.photo[-1]
    matrix_vision = MatrixVision(img.get_file().download_as_bytearray(), config.properties['fonts_path'], fps=30)
    log.info("Image has been downloaded.")
    user = update.message.from_user
    animation_file_name = f"{user['id']}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.mp4"
    matrix_vision.run(animation_file_name)
    with open(animation_file_name, 'rb') as animation:
        update.message.reply_animation(animation = animation)
    os.remove(animation_file_name)
    log.info(f"Remove temporary file {animation_file_name}")



def reply_to_document(update: Update, context: CallbackContext):
    """Send echo photo to user."""
    update.message.reply_text("Image is expected!")


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    log.warning(f'Update {update} caused error {context.error}')
    update.message.reply_text('Something happened, please try again later.')


def main():
    global_config = Config(file_path='config.json')
    updater = Updater(global_config.properties['token'], use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))

    # add replies for image, documents and text messages on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, functools.partial(reply_to_image, config = global_config)))
    updater.dispatcher.add_handler(MessageHandler(Filters.document, reply_to_document))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, reply_to_text))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    log.info('Start Bot')
    main()
