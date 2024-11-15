from telegram.ext import Updater, MessageHandler, CommandHandler, Application, ContextTypes
from telegram import Update
import threading
import time
import const

# Define a global variable to store the response
response = None
updater = None


def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global response
    global updater

    if "image" in update.message.text:
        response = update.message.text  # Store the user's response
        updater.stop()


def start_bot_thread():
    def start_bot():
        global updater
        updater = Application.builder().token(const.telegrambottoken).build()

        # Message handler without using Filters
        updater.add_handler(MessageHandler(None, handle_response))  # None: captures all messages

        updater.run_polling(allowed_updates=Update.ALL_TYPES)

    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()


async def start_bot():
    global updater
    updater = Application.builder().token(const.telegrambottoken).build()

    # Message handler without using Filters
    updater.add_handler(MessageHandler(None, handle_response))  # None: captures all messages

    await updater.run_polling(allowed_updates=Update.ALL_TYPES)


# Wait for the user's response in the main thread
def wait_for_response(timeout=60):
    global response
    response = None  # Reset response
    start_time = time.time()
    to_return = response
    response = None
    while time.time() - start_time < timeout:
        if to_return:
            print("message_received")
            return to_return
        time.sleep(1)
    return None  # Timeout if no response