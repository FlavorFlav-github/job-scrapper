from telegram.ext import Updater, MessageHandler, CommandHandler, Application, ContextTypes
from telegram import Update
import threading
import time
import const
import asyncio

response = None


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.updater = None
        self.response = None
        self.running = True

    async def handle_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        global response
        if "image" in update.message.text:
            print("Message Received")
            response = update.message.text
            self.running = False
            await self.updater.stop()

    async def run_bot(self):
        self.updater = Application.builder().token(self.token).build()

        # Message handler without using Filters
        self.updater.add_handler(MessageHandler(None, self.handle_response))

        await self.updater.initialize()
        await self.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        # Keep the bot running until self.running becomes False
        while self.running:
            await asyncio.sleep(1)

        await self.updater.stop()


def start_bot_async():
    bot = TelegramBot(const.telegrambottoken)

    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the bot in the background
    future = asyncio.run_coroutine_threadsafe(bot.run_bot(), loop)

    return bot, future, loop


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