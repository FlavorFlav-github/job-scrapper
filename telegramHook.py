from telegram.ext import Updater, MessageHandler, CommandHandler, Application, ContextTypes
from telegram import Update
import threading
import time
import const
import asyncio

# Define a global variable to store the response
response = None
updater = None


def start_bot_thread():
    def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global response
        global updater

        if "image" in update.message.text:
            response = update.message.text  # Store the user's response
            updater.stop()

    async def run_bot():
        global updater
        updater = Application.builder().token(const.telegrambottoken).build()

        # Message handler without using Filters
        updater.add_handler(MessageHandler(None, handle_response))  # None: captures all messages

        await updater.initialize()
        await updater.run_polling(allowed_updates=Update.ALL_TYPES)

    def thread_target():
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the bot
        loop.run_until_complete(run_bot())
        loop.close()

    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=thread_target)
    bot_thread.start()
    return bot_thread


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