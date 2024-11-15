from telegram.ext import Updater, MessageHandler, CommandHandler
import threading
import time
import const

# Define a global variable to store the response
response = None
updater = None


def handle_response(update, context):
    global response
    global updater

    if "Image" in update.message.text:
        response = update.message.text  # Store the user's response
        updater.stop()
    context.bot.send_message(chat_id=update.effective_chat.id, text="Response received!")


def start_bot_thread():
    global updater

    def start_bot():
        updater = Updater(token=const.telegrambottoken, use_context=True)
        dispatcher = updater.dispatcher

        # Message handler without using Filters
        dispatcher.add_handler(MessageHandler(None, handle_response))  # None: captures all messages

        updater.start_polling()
        updater.idle()

    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()


# Wait for the user's response in the main thread
def wait_for_response(timeout=60):
    global response
    response = None  # Reset response
    start_time = time.time()
    to_return = response
    response = None
    while time.time() - start_time < timeout:
        if to_return:
            return to_return
        time.sleep(1)
    return None  # Timeout if no response